import unittest
from datetime import datetime, timedelta

import toolkit.process as process


class TestNormalizeDatetimes(unittest.TestCase):
    
    def testMonthlyNormalize(self):
        self.annualClean = [datetime(2000, x, 1) for x in range(1, 12)]
        self.annualFifteenth = [datetime(2000, x, 15) for x in range(1, 12)]
        self.monthly = 'monthly'
        self.normalDates = process.normalizeDatetimes(self.annualFifteenth, self.monthly)
        self.assertEqual(self.normalDates, self.annualClean)
    
    def testDailyNormalize(self):
        self.dailyClean = [datetime(2000, 1, 1, 0, 0) + timedelta(days=x) for x in range(0, 5)]
        self.dailyNoonish = [datetime(2000, 1, 1, 12, 15) + timedelta(days=x) for x in range(0, 5)]
        self.daily = 'daily'
        self.normalDaily = process.normalizeDatetimes(self.dailyNoonish, self.daily)
        self.assertEqual(self.dailyClean, self.normalDaily)
        
        
if __name__ == '__main__':
    unittest.main()
         