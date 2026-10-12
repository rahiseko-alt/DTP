import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "check-school-comparison.py"
spec = importlib.util.spec_from_file_location("check_school_comparison", SCRIPT)
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)
builder = chk.builder


def make_files(tmp, own_rows, ref_rows, regenerate=True):
    own = Path(tmp) / "own.md"
    ref = Path(tmp) / "ref.md"
    out = Path(tmp) / "out.md"
    own.write_text("| 項目 | 記録 |\n| --- | --- |\n" + "\n".join(f"| {k} | {v} |" for k, v in own_rows.items()) + "\n", encoding="utf-8")
    ref.write_text("| 項目 | A | B | C |\n| --- | --- | --- | --- |\n" + "\n".join(f"| {k} | {a} | {b} | {c} |" for k, (a, b, c) in ref_rows.items()) + "\n", encoding="utf-8")
    if regenerate:
        out.write_text(builder.render(builder.read_table(own), builder.read_table(ref)), encoding="utf-8")
    else:
        out.write_text("古い内容\n", encoding="utf-8")
    return own, ref, out


def full_rows():
    own = {k: "x" for _, _, ol in builder.ROWS for k in ol}
    ref = {rl: ("a", "b", "c") for _, rl, _ in builder.ROWS}
    return own, ref


class CheckSchoolComparisonTest(unittest.TestCase):
    def test_clean_files_pass(self):
        own, ref = full_rows()
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = chk.check(*make_files(tmp, own, ref))
        self.assertEqual(errors, [])

    def test_stale_comparison_is_error(self):
        own, ref = full_rows()
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = chk.check(*make_files(tmp, own, ref, regenerate=False))
        self.assertTrue(any("最新ではありません" in e for e in errors))

    def test_missing_reference_label_is_error(self):
        own, ref = full_rows()
        del ref["学校名"]
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = chk.check(*make_files(tmp, own, ref))
        self.assertTrue(any("参考校台帳の項目「学校名」" in e for e in errors))

    def test_missing_own_label_is_error(self):
        own, ref = full_rows()
        del own["住所"]
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = chk.check(*make_files(tmp, own, ref))
        self.assertTrue(any("確定台帳の項目「住所」" in e for e in errors))

    def test_bank_account_number_is_error(self):
        own, ref = full_rows()
        ref["電話"] = ("普通預金 No.1234567", "b", "c")
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = chk.check(*make_files(tmp, own, ref))
        self.assertTrue(any("口座番号" in e for e in errors))

    def test_wrong_column_count_is_error(self):
        own, ref = full_rows()
        with tempfile.TemporaryDirectory() as tmp:
            own_p, ref_p, out_p = make_files(tmp, own, ref)
            ref_p.write_text(ref_p.read_text(encoding="utf-8") + "| 壊れた行 | a | b |\n", encoding="utf-8")
            errors, _ = chk.check(own_p, ref_p, out_p)
        self.assertTrue(any("列数" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
