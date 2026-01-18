"""Tests for iCalendar generation."""

import unittest

from app.ical_generator import generate_ical, _group_consecutive_slots


class TestGroupConsecutiveSlots(unittest.TestCase):
    
    def test_empty_list(self):
        self.assertEqual(_group_consecutive_slots([]), [])

    def test_single_slot(self):
        self.assertEqual(_group_consecutive_slots([540]), [[540]])  # 9:00

    def test_consecutive_slots(self):
        # 9:00, 9:15, 9:30
        self.assertEqual(_group_consecutive_slots([540, 555, 570]), [[540, 555, 570]])

    def test_non_consecutive_slots(self):
        # 9:00, 10:00, 11:00
        self.assertEqual(_group_consecutive_slots([540, 600, 660]), [[540], [600], [660]])

    def test_mixed_slots(self):
        # 9:00, 9:15, 9:30, 10:30, 10:45, 12:00
        self.assertEqual(
            _group_consecutive_slots([540, 555, 570, 630, 645, 720]), 
            [[540, 555, 570], [630, 645], [720]]
        )


class TestGenerateIcal(unittest.TestCase):
    
    def _empty_selections(self):
        """Helper to create empty selections dict."""
        return {day: [] for day in [
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 
            'Friday', 'Saturday', 'Sunday'
        ]}

    def test_empty_selections(self):
        ical = generate_ical(self._empty_selections())
        self.assertIn('BEGIN:VCALENDAR', ical)
        self.assertIn('END:VCALENDAR', ical)
        self.assertNotIn('BEGIN:VEVENT', ical)

    def test_single_slot_selection(self):
        selections = self._empty_selections()
        selections['Monday'] = [{'hour': 9, 'minute': 0}]
        ical = generate_ical(selections, 'Test Room')
        self.assertIn('BEGIN:VEVENT', ical)
        self.assertIn('Test Room - Occupied', ical)

    def test_custom_space_name(self):
        selections = self._empty_selections()
        selections['Monday'] = [{'hour': 9, 'minute': 0}]
        ical = generate_ical(selections, 'Conference Room B')
        self.assertIn('Conference Room B', ical)

    def test_ical_format_compliance(self):
        selections = self._empty_selections()
        selections['Monday'] = [{'hour': 9, 'minute': 0}, {'hour': 9, 'minute': 15}]
        ical = generate_ical(selections)
        
        # Check required iCalendar fields
        self.assertIn('VERSION:2.0', ical)
        self.assertIn('PRODID:', ical)
        self.assertIn('DTSTART:', ical)
        self.assertIn('DTEND:', ical)
        self.assertIn('UID:', ical)

    def test_consecutive_slots_merged(self):
        selections = self._empty_selections()
        # 9:00, 9:15, 9:30, 9:45 should become one event
        selections['Monday'] = [
            {'hour': 9, 'minute': 0},
            {'hour': 9, 'minute': 15},
            {'hour': 9, 'minute': 30},
            {'hour': 9, 'minute': 45}
        ]
        ical = generate_ical(selections)
        # Should only have one VEVENT
        self.assertEqual(ical.count('BEGIN:VEVENT'), 1)


if __name__ == '__main__':
    unittest.main()