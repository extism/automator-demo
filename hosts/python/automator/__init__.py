from typing import Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import os
import json
import extism
import threading
import time

@dataclass
class TriggerArgument:
    name: str
    description: str
    type: str

@dataclass
class Trigger:
    name: str
    description: str
    arguments: Optional[list[TriggerArgument]] = None

@dataclass
class ActionArgument:
    name: str
    description: str
    type: str

@dataclass
class Action:
    name: str
    arguments: list[ActionArgument]

@dataclass_json
@dataclass
class PluginAction:
    id: str
    args: dict

    @property
    def plugin(self):
        plugin_name, _ = self.id.split("#")
        return plugin_name

    @property
    def function(self):
        _, action_name = self.id.split("#")
        return action_name


@dataclass_json
@dataclass
class PluginMetadata:
    name: str
    type: str
    poll_time: Optional[int] = 0
    actions: Optional[list[Action]] = None
    triggers: Optional[list[Trigger]] = None

class PluginManifest:
    path: str
    module_data: bytes
    metadata: PluginMetadata

    def __init__(self, path: str) -> None:
        self.path = path
        self.module_data = open(self.path, "rb").read()
        # we only need a temporary context to load the plugin metadata
        with extism.Context() as ctx:
            plugin = ctx.plugin(self.module_data, wasi=True)
            self.metadata = PluginMetadata.from_json(plugin.call("get_metadata", ""))

class Plugin:
    manifest: PluginManifest

    def __init__(self, manifest: PluginManifest) -> None:
        self.manifest = manifest
        self.ctx = extism.Context()
        self.plugin = self.ctx.plugin(self.manifest.module_data, wasi=True)
    
    def call(self, func: str, data: str ="", cast=lambda x: x) -> any:
        print(f"Calling {self.manifest.metadata.name}#{func} with {data}")
        return cast(self.plugin.call(func, data))

    def free(self):
        self.ctx.free()

class Service(threading.Thread):
    callback: callable
    action: PluginAction
    plugin: Plugin

    def __init__(self, plugin: Plugin) -> None:
        self.plugin = plugin
        self.poll_time = plugin.manifest.metadata.poll_time
        threading.Thread.__init__(self)

    def register(self, action: PluginAction, callback: callable) -> None:
        self.action = action
        self.callback = callback

    def run(self):
        while True:
            result = self.plugin.call(self.action.function, json.dumps(self.action.args))
            self.callback(result)
            print(f"Sleeping for {self.poll_time}")
            time.sleep(self.poll_time / 1000)

class PluginRegistry:
    plugins: list[PluginManifest]

    def __init__(self, plugin_path: str) -> None:
        self.plugins = []
        for filename in os.listdir(plugin_path):
            f = os.path.join(plugin_path, filename)
            if os.path.isfile(f) and filename.endswith(".wasm"):
                self.plugins.append(PluginManifest(f))
        
    def execute_action(self, action_id: str, data: str) -> None:
        plugin_name, action_name = action_id.split("#")
        manifest = next(p for p in self.plugins if p.metadata.name == plugin_name)
        if not manifest:
            raise "Couldnt find plugin"
        
        plugin = Plugin(manifest)

        action = next(a for a in plugin.manifest.metadata.actions if a.name == action_name)
        if not action:
            raise "Couldnt find action"

        result = plugin.call(action_name, data)
        del plugin
        return result

    def get_service(self, action: PluginAction) -> Service:
        manifest = next(p for p in self.plugins if p.metadata.name == action.plugin)
        if not manifest:
            raise "Couldnt find plugin"
        return Service(Plugin(manifest))

@dataclass_json
@dataclass
class App:
    id: str
    trigger: PluginAction
    filters: list[str]
    action: str

@dataclass_json
@dataclass
class Apps:
    apps: list[App]

plugins = PluginRegistry("../../plugins/compiled")

def init_app(app: App) -> Service:
    def on_trigger(result):
        # for f in app.filters:
        #     result = plugins.execute_action(f, result)
        plugins.execute_action(app.action, result)

    service = plugins.get_service(app.trigger)
    service.register(app.trigger, on_trigger)
    return service

with open("../../apps.json", "r") as f:
    apps = Apps.schema().loads(f.read())

print(apps)
threads = [init_app(a) for a in apps.apps]

print("Started app threads")
for t in threads:
    t.start()

print("waiting on threads")
for t in threads:
    t.join()



