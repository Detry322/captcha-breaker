import opentuner
from opentuner.measurement import MeasurementInterface
from opentuner.resultsdb.models import Result
from opentuner.search.manipulator import ConfigurationManipulator, BooleanParameter, IntegerParameter
from opentuner.search.objective import MaximizeAccuracyMinimizeSize

from captchabreaker import score_multiple

best = (0, 100)

def is_better(old, new):
    return new[0] > old[0] or (new[0] == old[0] and new[1] < old[1])

class CaptchaTuner(MeasurementInterface):

    def run(self, desired_result, input, limit):
        cfg = desired_result.configuration.data
        print "Running..."
        _, correct, incorrect, size = score_multiple(cfg)
        global best
        if is_better(best, (correct, incorrect)):
            best = (correct, incorrect)
            print best, cfg
        return Result(time=0.0,
                      accuracy=(float(correct)/size),
                      size=incorrect)

    def manipulator(self):
        manipulator = ConfigurationManipulator()
        manipulator.add_parameter(IntegerParameter('pixeldiff_similarity_cutoff', 20, 50))
        manipulator.add_parameter(IntegerParameter('min_max_colorful_cutoff', 5, 20))
        manipulator.add_parameter(IntegerParameter('filter_grayscale_cutoff', 170, 215))
        manipulator.add_parameter(IntegerParameter('black_and_white_grayscale_cutoff', 170, 215))
        manipulator.add_parameter(IntegerParameter('count_around_delete_cutoff', 2, 4))
        manipulator.add_parameter(IntegerParameter('count_around_add_cutoff', 2, 5))
        manipulator.add_parameter(IntegerParameter('conway_many_count', 0, 5))
        manipulator.add_parameter(BooleanParameter('overlay'))
        return manipulator

    def save_final_config(self, configuration):
        cfg = configuration.data
        print "Final: ", cfg
        self.manipulator().save_to_file(configuration.data,
                                    'final_config.json')

    def objective(self):
        # we could have also chosen to store 1.0 - accuracy in the time field
        # and use the default MinimizeTime() objective
        return MaximizeAccuracyMinimizeSize()


if __name__ == '__main__':
    argparser = opentuner.default_argparser()
    CaptchaTuner.main(argparser.parse_args())
