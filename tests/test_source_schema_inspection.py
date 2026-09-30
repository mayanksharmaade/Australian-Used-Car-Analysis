from etl.profiling.inspect_source_schemas import sql_safe_name


def test_sql_safe_name():
    assert sql_safe_name("Fuel Consumption") == "Fuel_Consumption"
    assert sql_safe_name("CO2 (g/km)") == "CO2_g_km"
    assert sql_safe_name("2024 Value") == "Col_2024_Value"
