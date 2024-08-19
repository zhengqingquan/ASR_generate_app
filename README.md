# ASR_generate_app

Script used to generate APP on ASR platform.

## usage

Use in the root directory or evb folder:

```CMD
generate_app.py app_name asr-480x960
```

or

```CMD
generate_app.exe app_name asr-480x960
```

The first parameter represents the name of the APP to be created, and the second parameter represents the screen resolution.

## environment

The exe environment is:

```TEXT
Python 3.12.0
```

This exe is packaged based on the following:

```TEXT
pyinstaller 6.9.0
```

```CMD
pyinstaller --onefile --name generate_app generate_app.py
```