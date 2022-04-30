# garmin-workouts-cli

This unnofficial utility is for Garmin users to create workouts from text files, instead clicking in the official Garmin modern web application or another application.

## Development

Create a development environment:

```console
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv)$ python -m pip install -r requirements.txt
```

## Installation

TODO

## Config

```ini
[auth]
username=username@email.com
password=secret_password
```

## Quick Examples

```console
$ python garmin_workouts/garminworkouts.py login
```

Export the first 10 runs:

```console
python ./garmin_workouts/garminworkouts.py export --runs --limit 10
```

Import the workout with a name `workout.yml`:

```yaml
name: 'W17 - LT 6/13km'
steps:
  - type: warmup
    distance: 4000
    hr_low: 137
    hr_high: 156
  - type: run
    distance: 6000
    hr_low: 157
    hr_high: 174
  - type: cooldown
    distance: 3000
    hr_low: 137
    hr_high: 156
```

```console
python ./garmin_workouts/garminworkouts.py import -f workout.yml
```

## Usage

```console
garmin-workouts --help

usage: garmin-workouts [-v] [-h] COMMAND ...

Options:
  -v, --verbose  Increase output verbosity
  -h, --help     Show this help message and exit

Commands:
  COMMAND
    login        Log in to the Garmin Connect
    logout       Log out from the Garmin Connect
    export       Export workouts from the Garmin Connect to the file
    import       Import workouts to the Garmin Connect from a file
    rm (remove)  Remove one or more workouts from Garmin Connect
```

### `rm|remove`

```console
usage: garmin-workouts rm [-h] [--all] [--all-runs] [--force] [--helper-file FILE] [--name NAME] [--regex REG] [--id ID] [WORKOUT_ID [WORKOUT_ID ...]]

positional arguments:
  WORKOUT_ID           The ID of workout to remove

optional arguments:
  -h, --help           show this help message and exit
  --all                Remove all workouts
  --all-runs           Remove all run workouts
  --force, -f          Don't prompt before removal
  --name NAME          The name of workout to remove (can be defined multiple times)
  --regex REG, -r REG  All workouts with name matching this regex will be deleted
  --id ID              The ID of workout to remove (can be defined multiple times)
```

```
python garmin_workouts/garminworkouts.py rm --all-runs
```
