import datetime


def get_post_timing():
    current_day = datetime.date.today().strftime("%d")
    current_month = datetime.date.today().strftime("%B")
    current_year = datetime.date.today().strftime("%Y")

    return f"{current_month} {current_day}, {current_year}"


if __name__ == "__main__":
    current_time = get_post_timing()
    print(current_time)
