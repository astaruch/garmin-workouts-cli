import logging

from libs.garmin_api_client import GarminApiClient

log = logging.getLogger(__name__)


class Remove():
    def __init__(self, args, session):
        self.api_client = GarminApiClient(session=session)
        self._workouts_id = []
        # Prompt before deleting when `--force` is not defined
        self._prompt = False if args.remove_force else True
        self._parse_args(args)
        self._remove()

    def _parse_args(self, args):
        """
        Build the list of workout IDs, that we will call
        the Garmin Api Client with.

        If there is file with mapping WORKOUT_NAME:WORKOUT_ID
        defined, and there is deletion by name, we don't need
        to call API to get list of workouts info.

        Otherwise we need to query it.

        Don't allow different ways at the same time.
        """
        print(args)
        log.info(args)
        # 1. Add positional IDs ([WORKOUT_ID [WORKOUT_ID ...]])
        if args.WORKOUT_ID:
            for workout_id in args.WORKOUT_ID:
                self._workouts_id.append(workout_id)

        # 2. Add optional IDs ([--id ID [--id ID ...])
        if args.remove_workout_id_optional:
            for workout_id in args.remove_workout_id_optional:
                self._workouts_id.append(workout_id)

        # TODO: Other cases

    def _remove(self):
        for workout_id in self._workouts_id:
            if self._prompt:
                workout_url = self.api_client.get_workout_url(workout_id)
                prompt_message = f"Are you sure you want to delete '{workout_url}'? [y/N]"
                answer = input(prompt_message) or "n"
                if answer.lower() == "n":
                    continue
                elif answer.lower() == "y":
                    pass
                else:
                    print("Unexpected input. Skipping..")

            self.api_client.delete_workout(workout_id)
