.PHONY: build

build:
	cargo build --release --target wasm32-wasi
	cp target/wasm32-wasi/release/*.wasm plugins/compiled

run:
	cd hosts/python && poetry run python automator/__init__.py
