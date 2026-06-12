#!/usr/bin/env python3
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PolicyModalClosePositionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.css=(ROOT/"assets/css/policy-modal-overrides.css").read_text(encoding="utf-8")
 def test_close_button_is_pinned_to_upper_right(self):
  for token in ["position: absolute !important;","top: 12px !important;","right: 12px !important;","bottom: auto !important;","left: auto !important;"]: self.assertIn(token,self.css)
 def test_close_button_is_circular_icon_control(self):
  for token in ["width: 32px !important;","height: 32px !important;","border-radius: 50% !important;","padding: 0 !important;"]: self.assertIn(token,self.css)
  self.assertNotIn("padding: 0 11px;",self.css)
if __name__=="__main__": unittest.main()
