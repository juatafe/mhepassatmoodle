import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location('connector', Path(__file__).resolve().parents[1] / 'scripts/aules_chrome.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
URL = 'https://aules.edu.gva.es/semipresencial/course/view.php?id=123'

class ConnectorTests(unittest.TestCase):
    def test_target_validation(self):
        self.assertEqual(c.course_url(URL), URL)
        for bad in (URL.replace('https:', 'ftp:'), URL.replace('aules.edu.gva.es', ''),
                    URL.replace('123', 'x'), URL + '&sesskey=secret',
                    URL.replace('https://', 'https://user:password@')):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                c.course_url(bad)

    def test_accepts_other_moodle_sites_and_base_paths(self):
        for url in ('https://campus.example.org/course/view.php?id=7',
                    'https://campus.example.org/moodle/course/view.php?id=7',
                    'http://localhost:8080/moodle/course/view.php?id=7',
                    'http://[::1]:8080/course/view.php?id=7'):
            with self.subTest(url=url):
                self.assertEqual(c.course_url(url), url)
                self.assertEqual(c.Session(url).base, url.split('/course/view.php')[0] + '/')
                self.assertEqual(c.clean_url(url + '&sesskey=SECRET'), url)

    def test_authenticated_course_on_another_domain(self):
        url = 'https://campus.example.org/moodle/course/view.php?id=7'
        session = c.Session(url)
        session.page = Mock()
        session.page.url = url
        session.page.goto.return_value.status = 200
        session.page.evaluate.return_value = 7
        session.page.locator.side_effect = lambda selector: Mock(count=Mock(return_value=1 if 'logout.php' in selector else 0))
        self.assertIs(session.open_course(), session.page)
        session.page.url = 'https://other.example.org/moodle/course/view.php?id=7'
        with self.assertRaises(RuntimeError):
            session.open_course()

    def test_diagnostics_remove_auth_queries_and_userinfo(self):
        self.assertEqual(c.clean_url('https://user:secret@aules.edu.gva.es/x?id=4&sesskey=SECRET&code=TOKEN#secret'),
                         'https://aules.edu.gva.es/x?id=4')

    def test_endpoint_stays_local(self):
        self.assertEqual(c.endpoint(9222), 'http://127.0.0.1:9222')
        for bad in (0, 80, 65536):
            with self.assertRaises(ValueError):
                c.endpoint(bad)

    def test_cleanup_preserves_user_browser(self):
        session = c.Session(URL)
        session.page, session.pw, session.browser = Mock(), Mock(), Mock()
        session.__exit__(None, None, None)
        session.page.close.assert_called_once()
        session.pw.stop.assert_called_once()
        session.browser.close.assert_not_called()

    def test_login_tab_can_stay_open(self):
        session = c.Session(URL)
        session.page, session.pw = Mock(), Mock()
        session.keep_page = True
        session.__exit__(None, None, None)
        session.page.close.assert_not_called()
        session.pw.stop.assert_called_once()

    def test_failed_tab_cleanup_still_disconnects(self):
        session = c.Session(URL)
        session.page, session.pw = Mock(), Mock()
        session.page.close.side_effect = RuntimeError('closed')
        with self.assertRaises(RuntimeError):
            session.__exit__(None, None, None)
        session.pw.stop.assert_called_once()

    def test_rejects_login_and_wrong_course(self):
        for final_url, course_id in ((URL.replace('course/view.php', 'login/index.php'), 123), (URL, 99)):
            session = c.Session(URL)
            session.page = Mock()
            session.page.goto.return_value.status = 200
            session.page.url = final_url
            session.page.locator.return_value.count.return_value = 0
            session.page.evaluate.return_value = course_id
            with self.assertRaises(RuntimeError):
                session.open_course()

if __name__ == '__main__':
    unittest.main()
