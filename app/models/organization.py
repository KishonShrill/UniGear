from app.utils.db import get_db_cursor


class Organization:
    COLLEGE_CODE_MAP = {
        "cass": 1,
        "cba": 2,
        "ccs": 3,
        "ced": 4,
        "coe": 5,
        "chs": 6,
        "csm": 7,
    }

    def __init__(self, org_id=None, org_name=None, college_id=None):
        self.org_id = org_id
        self.org_name = org_name
        self.college_id = college_id

    @classmethod
    def get_by_college_code(cls, college_code):
        """Retrieve all student organizations under a college by college code."""
        college_id = cls.COLLEGE_CODE_MAP.get(college_code.lower())
        if not college_id:
            return None
        return cls.get_by_college_id(college_id)

    @staticmethod
    def get_by_college_id(college_id):
        """Retrieve all student organizations belonging to a specific college.

        Prioritizes the Executive Council at the top, then alphabetical order.
        """
        query = """
            SELECT org_id, org_name
            FROM organization
            WHERE college_id = %s
            ORDER BY
                CASE WHEN org_name LIKE '%%Executive Council%%' THEN 1 ELSE 2 END,
                org_name ASC;
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (college_id,))
            rows = cursor.fetchall()
            return [{"id": row[0], "name": row[1]} for row in rows]
