#This function is being used for the line charts so that the charts are generated properly.
def convert_line_date_format(date_str):
    month_mapping = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
    }
    parts = date_str.split('-')
    if len(parts) != 2:
        return date_str  # Return the original string if it doesn't match the expected format
    year, month_name = parts
    month = month_mapping.get(month_name)
    if not month:
        return date_str  # Return the original string if month_name is not in the mapping
    return f"{year}-{month}-01"