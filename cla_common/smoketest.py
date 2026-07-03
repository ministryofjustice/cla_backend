import os
import unittest


def smoketest(testcase_class):

    suite = unittest.TestLoader().loadTestsFromTestCase(testcase_class)
    result = unittest.TestResult()
    suite.run(result)

    status = "failure"
    if result.wasSuccessful():
        status = "success"

    version = os.popen("git describe --abbrev=0").read().strip()

    def format_result(test):
        test, output = test
        return {"name": test._testMethodName, "doc": test._testMethodDoc, "output": output}

    return {
        "result": {
            "tag": version,
            "status": status,
            "tests_run": result.testsRun,
            "detail": {"errors": map(format_result, result.errors), "failures": map(format_result, result.failures)},
        }
    }
