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
## Usage

Check the help page!

```console
$ python garmin_workouts/garminworkouts.py -h
```

## Config

```ini
[auth]
username=username@email.com
password=secret_password
```

## Examples

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
