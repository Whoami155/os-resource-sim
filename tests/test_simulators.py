import unittest
from simulators import cpu_schedule,compare_cpu,memory_allocate,disk_schedule,bankers_algorithm
class TestOS(unittest.TestCase):
 def setUp(self):self.p=[{'id':'P1','arrival':0,'burst':8,'priority':2},{'id':'P2','arrival':1,'burst':4,'priority':1},{'id':'P3','arrival':2,'burst':2,'priority':3}]
 def test_fcfs(self):self.assertEqual([x['waiting'] for x in cpu_schedule(self.p)['metrics']],[0,7,10])
 def test_sjf(self):self.assertEqual([x['id'] for x in cpu_schedule(self.p,'SJF')['timeline']],['P1','P3','P2'])
 def test_srtf(self):self.assertEqual(sum(x['waiting'] for x in cpu_schedule(self.p,'SRTF')['metrics']),8)
 def test_rr(self):self.assertEqual(cpu_schedule(self.p,'RR',2)['summary']['makespan'],14)
 def test_idle(self):self.assertEqual(cpu_schedule([{'id':'X','arrival':5,'burst':2}])['summary']['cpuUtilization'],28.57)
 def test_compare(self):self.assertEqual(len(compare_cpu(self.p)),5)
 def test_memory(self):self.assertEqual([x['block'] for x in memory_allocate([100,500,200,300,600],[212,417,112,426],'BEST')['allocations']],[4,2,3,5])
 def test_disk_fcfs(self):self.assertEqual(disk_schedule([82,170,43,140,24,16,190],50,'FCFS')['summary']['totalSeek'],642)
 def test_disk_sstf(self):self.assertEqual(disk_schedule([82,170,43,140,24,16,190],50,'SSTF')['summary']['totalSeek'],208)
 def test_safe(self):self.assertTrue(bankers_algorithm([3,3,2],[[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]],[[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]])['safe'])
 def test_unsafe(self):self.assertFalse(bankers_algorithm([0],[[1],[1]],[[2],[2]])['safe'])
 def test_invalid(self):
  with self.assertRaises(ValueError):cpu_schedule([{'id':'X','burst':0}])
  with self.assertRaises(ValueError):disk_schedule([999],50)
if __name__=='__main__':unittest.main()
