# PPMTeams

A website I designed to track ppm teams for my cross-country team.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install packages.

```bash
pip install -r requirements.txt
```

## Configuration

Change the ```config.properties.example``` file to ```config.properties```.

```bash
[variables]
mongourl=
database=

[config]
analytics=false
```
Add the variables to the config file. Change config to desired values.

## Startup

Run the command ```hypercorn main:app``` to run the website. If you want to run it on a specific host and port add ```-b="{host}:{port}``` to the end of the command.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
