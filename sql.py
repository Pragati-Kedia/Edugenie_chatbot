# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker

# def get_period_dates(fy, pem):
#     """Return Period Start Date and Period End Date based on PEM and FY."""
#     period_mapping = {
#         3: (f"{fy}-01-01", f"{fy}-03-31"),
#         6: (f"{fy}-04-01", f"{fy}-06-30"),
#         9: (f"{fy}-07-01", f"{fy}-09-30"),
#         12: (f"{fy}-10-01", f"{fy}-12-31")
#     }
#     return period_mapping.get(pem, (None, None))

# # Database connection setup
# DATABASE_URL = "postgresql://postgres:12345@localhost:5432/testing"  # Update with actual DB details
# engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)
# session = Session()

# def insert_fs_header():
#     """Get user input, calculate period dates, and insert data into FS Header Test."""
    
#     pem = int(input("Enter PEM (3, 6, 9, 12): "))
#     fy = input("Enter Financial Year (e.g., 2025): ")

#     period_start, period_end = get_period_dates(fy, pem)
#     if not period_start or not period_end:
#         print("Invalid PEM value. Choose from 3, 6, 9, or 12.")
#         return
    
#       # Format PEM to be two digits with leading zero if necessary
#     pem_str = f"{pem:02d}"  
    
#     try:
#         query = text('''
#         INSERT INTO "FS Header Copy"
#         (
#             "Company Code",
#             "Company Symbol",
#             "Period Start Date",
#             "Period End Date",
#             "Financial Year",
#             "PEM",
#             "Nature Of Report",
#             "FS Header Id"
#         )
#         SELECT DISTINCT ON (co."Company Code", st."Nature Of Report")
#             co."Company Code",
#             co."Company Symbol",
#             :period_start,
#             :period_end,
#             :fy,
#             :pem,
#             st."Nature Of Report",
#             co."Company Code" || :fy || :pem_str AS "FS Header Id"
#         FROM public."Staging" st
#         JOIN public."Company" co
#             ON st."Company Code" = co."Company Code";
#         ''')
        
#        # Pass pem_str to the query
#         session.execute(query, {
#             "period_start": period_start,
#             "period_end": period_end,
#             "fy": fy,
#             "pem": pem,
#             "pem_str": pem_str  # Pass the formatted pem_str
#         })
#         session.commit()
#         print("Data inserted successfully into FS Header Demo.")

#     except Exception as e:
#         print("Error:", e)
#         session.rollback()
#     finally:
#         session.close()

# if __name__ == "__main__":
#     insert_fs_header()



# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker

# def get_period_dates(fy, pem):
#     """Return Period Start Date and Period End Date based on PEM and FY."""
#     period_mapping = {
#         3: (f"{fy}-01-01", f"{fy}-03-31"),
#         6: (f"{fy}-04-01", f"{fy}-06-30"),
#         9: (f"{fy}-07-01", f"{fy}-09-30"),
#         12: (f"{fy}-10-01", f"{fy}-12-31")
#     }
#     return period_mapping.get(pem, (None, None))

# # Database connection setup
# DATABASE_URL = "postgresql://postgres:12345@localhost:5432/testing"  # Update with actual DB details
# engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)
# session = Session()

# def insert_fs_header():
#     """Get user input, calculate period dates, and insert data into FS Header Copy & P&L YTD."""
    
#     pem = int(input("Enter PEM (3, 6, 9, 12): "))
#     fy = input("Enter Financial Year (e.g., 2025): ")

#     period_start, period_end = get_period_dates(fy, pem)
#     if not period_start or not period_end:
#         print("Invalid PEM value. Choose from 3, 6, 9, or 12.")
#         return

#     # Format PEM to be two digits with leading zero if necessary
#     pem_str = f"{pem:02d}"  

#     try:
#         # **Section 1: Insert into FS Header Copy**
#         query_fs_header = text('''
#         INSERT INTO "FS Header Copy"
#         (
#             "Company Code",
#             "Company Symbol",
#             "Period Start Date",
#             "Period End Date",
#             "Financial Year",
#             "PEM",
#             "Nature Of Report",
#             "FS Header Id"
#         )
#         SELECT DISTINCT ON (co."Company Code", st."Nature Of Report")
#             co."Company Code",
#             co."Company Symbol",
#             :period_start,
#             :period_end,
#             :fy,
#             :pem,
#             st."Nature Of Report",
#             co."Company Code" || :fy || :pem_str AS "FS Header Id"
#         FROM public."Staging" st
#         JOIN public."Company" co
#             ON st."Company Code" = co."Company Code";
#         ''')

#         session.execute(query_fs_header, {
#             "period_start": period_start,
#             "period_end": period_end,
#             "fy": fy,
#             "pem": pem,
#             "pem_str": pem_str
#         })
#         session.commit()
#         print("Data inserted successfully into FS Header Copy.")

#         # **Section 3: Insert into P&L YTD using dynamically generated FS Header Id**
#         query_pl_ytd = text('''
#         INSERT INTO "P&L YTD" (
#             "FS Header Id",
#             "Nature Of Report",
#             "Taxonomy_Id",
#             "Taxonomy Order",
#             "Company Code",
#             "Company Symbol",
#             "Financial Year",
#             "Quarter",
#             "PEM",
#             "Period Start Date",
#             "Period End Date",
#             "Element Name",
#             "Unit",
#             "Value",
#             "Decimal"
#         )
#         SELECT 
#             fs."FS Header Id", 
#             st."Nature Of Report",
#             st."Taxonomy_Id",
#             NULL,  -- Taxonomy Order set as NULL
#             st."Company Code",
#             fs."Company Symbol",
#             st."Financial Year",
#             st."Quarter",
#             st."PEM",
#             st."Period Start Date",
#             st."Period End Date",
#             st."Element Name",
#             st."Unit",
#             CAST(st."Value" AS NUMERIC),  -- Explicitly cast to NUMERIC
#             st."Decimal"
#         FROM public."Staging" st
#         JOIN public."FS Header Copy" fs 
#             ON st."Company Code" = fs."Company Code"
#             AND st."Financial Year" = fs."Financial Year"
#             AND st."PEM" = fs."PEM"
#         WHERE st."Taxonomy_Id" LIKE '100200.101%'  
#         AND st."Financial Year" = :fy  -- Dynamically using user input
#         AND st."PEM" = :pem;  -- Dynamically using user input
#         ''')

#         session.execute(query_pl_ytd, {
#             "fy": fy,
#             "pem": pem
#         })
#         session.commit()
#         print("Data inserted successfully into P&L YTD.")

#     except Exception as e:
#         print("Error:", e)
#         session.rollback()
#     finally:
#         session.close()

# if __name__ == "__main__":
#     insert_fs_header()


from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def get_period_dates(fy, pem):
    """Return Period Start Date and Period End Date based on PEM and FY."""
    period_mapping = {
        "3": (f"{fy}-01-01", f"{fy}-03-31"),
        "6": (f"{fy}-04-01", f"{fy}-06-30"),
        "9": (f"{fy}-07-01", f"{fy}-09-30"),
        "12": (f"{fy}-10-01", f"{fy}-12-31")
    }
    return period_mapping.get(pem, (None, None))

# Database connection setup
DATABASE_URL = "postgresql://postgres:12345@localhost:5432/copytesting"  # Update with actual DB details
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def insert_fs_header(fy, pem):
    """Insert FS Header ID into 'FS Header Copy' table based on user input."""
    
    session = Session()
    pem = str(pem)  # Convert PEM to string
    period_start, period_end = get_period_dates(fy, pem)

    if not period_start or not period_end:
        print("Invalid PEM value. Choose from 3, 6, 9, or 12.")
        return

    try:
        query = text('''
        INSERT INTO "FS Header"
        (
            "Company Code",
            "Company Symbol",
            "Period Start Date",
            "Period End Date",
            "Financial Year",
            "PEM",
            "Nature Of Report",
            "FS Header Id"
        )
        SELECT DISTINCT ON (co."Company Code", st."Nature Of Report")
            co."Company Code",
            co."Company Symbol",
            :period_start,
            :period_end,
            :fy,
            :pem,  -- PEM is now passed as a string
            st."Nature Of Report",
            co."Company Code" || :fy || :pem AS "FS Header Id"
        FROM public."Staging" st
        JOIN public."Company" co
            ON st."Company Code" = co."Company Code";
        ''')

        session.execute(query, {
            "period_start": period_start,
            "period_end": period_end,
            "fy": fy,
            "pem": pem
        })
        session.commit()
        print("Data inserted successfully into FS Header.")

    except Exception as e:
        print("Error inserting into FS Header:", e)
        session.rollback()
    finally:
        session.close()


def insert_pnl_ytd(fy, pem):
    """Insert FS Header ID into 'P&L YTD' table based on user input."""
    
    session = Session()
    pem = str(pem)  # Convert PEM to string

    try:
        query = text('''
        INSERT INTO "P&L YTD" (
            "FS Header Id",
            "Nature Of Report",
            "Taxonomy_Id",
            "Taxonomy Order",
            "Company Code",
            "Company Symbol",
            "Financial Year",
            "Quarter",
            "PEM",
            "Period Start Date",
            "Period End Date",
            "Element Name",
            "Unit",
            "Value",
            "Decimal"
        )
        SELECT
            fs."FS Header Id",
            st."Nature Of Report",
            st."Taxonomy_Id",
            NULL,  -- Taxonomy Order set as NULL
            st."Company Code",
            fs."Company Symbol",
            st."Financial Year",
            st."Quarter",
            st."PEM",
            st."Period Start Date",
            st."Period End Date",
            st."Element Name",
            st."Unit",
            CAST(st."Value" AS NUMERIC),  -- Explicitly cast to NUMERIC
            st."Decimal"
        FROM public."Staging" st
        JOIN public."FS Header" fs
            ON st."Company Code" = fs."Company Code"
            AND st."Financial Year" = fs."Financial Year"
            AND st."PEM" = fs."PEM"
        WHERE st."Taxonomy_Id" LIKE '100200.101%'
        AND st."Financial Year" = :fy  -- Dynamically using user input
        AND st."PEM" = :pem;  -- PEM passed as string
        ''')

        session.execute(query, {"fy": fy, "pem": pem})  # Pass PEM as string
        session.commit()
        print("Data inserted successfully into P&L YTD.")

    except Exception as e:
        print("Error inserting into P&L YTD:", e)
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    pem = input("Enter PEM (3, 6, 9, 12): ").strip()  # Keep PEM as string
    fy = input("Enter Financial Year (e.g., 2025): ").strip()

    insert_fs_header(fy, pem)  # Step 1: Insert into FS Header Copy
    insert_pnl_ytd(fy, pem)  # Step 2: Insert into P&L YTD
