from collections import defaultdict
from collections import deque


VERSION = "0.1.1"


class DictIQM():
    """Computes the Interquartile Mean (IQM) of a dictionary containing
    containing number buckets (key) and the count of their occurrences (value).

    The number bucket supports variable precision:

    - round_digits is the digit supplied to the round() function.
    - tenth_precise=True will round to one less digit for the lowest 10%.
      For example: round_digits=-2, tenth_precise would result in numbers less
      than 100 being rounded to to the nearest 10th.

    none_action determines how non-numbers are treated (all non-numbers are
    stored as None):

    - discard: discard them (default)
    - max: replace them with the maximum value
    - min: replace them with the minimum value

    This class is efficient for datasets in which many numbers are repeated.
    It should not be used for large datasets with a uniform distribution.
    """

    def __init__(self, round_digits=None, tenth_precise=None,
                 none_action=None):
        self.as_ints = False
        self.bound = None
        # round_digits
        if round_digits is None:
            round_digits = -1
        # tenth_precise
        if tenth_precise is None:
            tenth_precise = False
        elif tenth_precise:
            if round_digits >= 0:
                raise Exception("tenth_precise only applies to round_digits "
                                "< 0.")
            self.bound = abs(round_digits) * 10
        else:
            tenth_precise = False
        # as_ints
        if round_digits < 0:
            self.as_ints = True
        # none_action
        if none_action is None:
            none_action = "discard"
        elif none_action not in ("discard", "max", "min"):
            raise Exception("none_action must be one of 'discard', 'max', "
                            "or 'min'")
        self.data = defaultdict(self.prep_data)
        self.none_action = none_action
        self.round_digits = round_digits
        self.tenth_precise = tenth_precise

    def prep_data(self):
        if self.as_ints:
            return {"num_counts": defaultdict(int), "count": 0}
        else:
            return {"num_counts": defaultdict(float), "count": 0}

    def remove_quartile(self, quartile, numbers, num_counts):
        """Removes the first quartile from a dictionary containing containing
        number buckets (dict key) and the count of their occurrences
        (dict value).
        """
        for num in numbers:
            if num_counts[num] <= quartile:
                quartile = quartile - num_counts[num]
                del num_counts[num]
            elif num_counts[num] > quartile:
                num_counts[num] -= quartile
                quartile = 0
            if quartile == 0:
                return num_counts
        raise Exception("quartile was never decreased to zero")

    def compute_iqm(self, key):
        """Compute the IQM of a dictionary containing number buckets (dict key)
        and the count of their occurrences (dict value).
        """
        count = self.data[key]["count"]
        num_counts = self.data[key]["num_counts"]
        none_action = self.none_action
        # No-op on empty
        if not num_counts:
            return None
        # Handle None values
        if None in num_counts:
            none_count = num_counts[None]
            del num_counts[None]
            if none_action in ("max", "min"):
                numbers = num_counts.keys()
                numbers.sort()
                num_min = numbers[0]
                num_max = numbers[-1]
            if none_action is "max":
                num_counts[num_max] += none_count
            elif none_action is "min":
                num_counts[num_min] += none_count
            else:
                count -= none_count
        # Return average if there are too few numbers to quartile
        if count < 4:
            num_sum = 0
            for num in num_counts:
                num_sum += num * num_counts[num]
            # Interquartile mean
            avg = num_sum / count
            return avg
        # Remove top (ascending) quartile
        quartile = int(count * 0.25)
        numbers = num_counts.keys()
        numbers.sort()
        num_counts = self.remove_quartile(quartile, numbers, num_counts)
        # Remove bottom (descending) quartile
        numbers = num_counts.keys()
        numbers.sort(reverse=True)
        num_counts = self.remove_quartile(quartile, numbers, num_counts)
        # Interquartile count and sum
        iq_count = int(count * 0.5)
        iq_sum = 0
        for num in num_counts:
            iq_sum += num * num_counts[num]
        # Interquartile mean
        iqm = iq_sum / iq_count
        return iqm

    def __call__(self, key, num):
        """For the key provided, increment its num bucket (dict key) count
        (dict value)."""
        as_ints = self.as_ints
        bound = self.bound
        data = self.data
        num = num.strip()
        round_digits = self.round_digits
        tenth_precise = self.tenth_precise
        try:
            num = float(num.strip())
            if as_ints:
                if tenth_precise and num < bound:
                    num = round(num, (round_digits + 1))
                else:
                    num = round(num, round_digits)
                num = int(num)
            else:
                num = round(num, round_digits)
        except:
            num = None
        data[key]["num_counts"][num] += 1
        data[key]["count"] += 1


class MovingIQM():
    """Computes the moving average of the Interquartile Mean (IQM) of a deque
    computed each period.

    none_action determines how non-numbers are treated (all non-numbers are
    stored as None):

    - discard: discard them (default)
    - max: replace them with the maximum value
    - min: replace them with the minimum value

    This class sacrifices accuracy for speed and low memory usage.
    """

    def __init__(self, period, none_action=None):
        # none_action
        if none_action is None:
            none_action = "discard"
        elif none_action not in ("discard", "max", "min"):
            raise Exception("none_action must be one of 'discard', 'max', "
                            "or 'min'")
        self.none_action = none_action
        self.period = int(period)
        self.data = defaultdict(self.prep_data)

    def prep_data(self):
        return {"deck": deque("", self.period), "deck_count": 0,
                "iqm_count": 0, "iqm_sum": 0.0}

    def iqm_sum(self, key):
        """Compute the key's new iqm sum"""
        data = self.data[key]
        deck = sorted(data["deck"])
        none_action = self.none_action
        if data["deck_count"] == 0:
            return
        # Handle None values
        if None in deck:
            none_count = deck.count(None)
            while None in deck:
                deck.remove(None)
            if none_action in ("max", "min"):
                if none_action is "max":
                    num_max = deck[-1]
                    deck = deck + ([num_max] * none_count)
                else:  # min
                    num_min = deck[0]
                    deck = ([num_min] * none_count) + deck
            else:
                data["deck_count"] -= none_count
            deck.sort()
        # Return average if there are too few numbers to quartile
        if data["deck_count"] < 4:
            iqm = float(sum(deck) / data["deck_count"])
        else:
            # determine quartile (point that divides the deck into four
            # groups)
            quartile = int(0.25 * data["deck_count"])
            # discard the lowest 25% and highest 25%
            deck = deck[quartile:-quartile]
            # mean of the interquartile range
            iqm = sum(deck) / len(deck)
        data["iqm_sum"] += iqm
        data["iqm_count"] += 1
        data["deck_count"] = 0

    def final_report(self, key):
        """Compute the key's average IQM from the iqm_sum and iqm_count."""
        data = self.data[key]
        self.iqm_sum(key)
        iqm_avg = data["iqm_sum"] / data["iqm_count"]
        return iqm_avg

    def __call__(self, key, num):
        """For the key provided, add the num to its deque."""
        try:
            num = float(num.strip())
        except:
            num = None
        data = self.data[key]
        data["deck"].append(num)
        data["deck_count"] += 1
        if data["deck_count"] == self.period:
            self.iqm_sum(key)
