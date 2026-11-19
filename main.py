
import csv


def validate_sale(row):
    """Validate required fields and values """

    required_fields = ["Customer", "Item", "Qty", "Price Total"]

    for field in required_fields:
        if field not in row or row[field] is None or not str(row[field]).strip():
            return None, f"Missing {field}"

    qty = row["Qty"]
    customer = row["Customer"]

    try:
        qty = int(qty)
    except ValueError:
        return None, f"Invalid quantity: {row['Qty']}"

    if qty <= 0:
        return None, "Invalid quantity: must be positive"

    item = row["Item"]

    try:
        price = float(row["Price Total"])
    except ValueError:
        return None, f"Invalid price: {row['Price Total']}"

    if price < 0:
        return None, "Invalid price: cannot be negative"

    return (customer, item, qty, price), None


def update_summary(summary, item, qty, price):
    """Accumulate item totals"""

    if item not in summary:
        summary[item] = {"Qty": 0, "Price Total": 0.0}

    summary[item]["Qty"] += qty
    summary[item]["Price Total"] += price

    return summary


def log_error(file, line_number, row, reason, fieldnames):
    """Record invalid data and error details."""

    original_values = ",".join(
        "" if row.get(field) is None else str(row.get(field))
        for field in fieldnames
    )

    file.write(f"Line {line_number} | {reason} | {original_values}\n")


def read_sales():
    """Read and process source records """

    summary = {}
    total_qty = 0
    subtotal = 0.0
    invalid_count = 0

    with open("errors.log", "w", encoding="utf-8") as error_file:

        try:
            with open("sales.csv", "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                fieldnames = reader.fieldnames or []

                for line_number, row in enumerate(reader, start=2):

                    sale, reason = validate_sale(row)

                    if reason:
                        log_error(
                            error_file,
                            line_number,
                            row,
                            reason,
                            fieldnames
                        )
                        invalid_count += 1
                        continue

                    customer, item, qty, price = sale

                    summary = update_summary(summary, item, qty, price)

                    total_qty += qty
                    subtotal += price

        except FileNotFoundError:
            print("Error: sales.csv could not be found.")
            return summary, total_qty, subtotal, invalid_count

    return summary, total_qty, subtotal, invalid_count


def save_summary(summary):
    """Write grouped sales CSV """

    with open("sales_summary.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Item", "Qty", "Price Total"])

        for item, data in sorted(summary.items()):
            writer.writerow([
                item,
                data["Qty"],
                f"{data['Price Total']:.2f}"
            ])


def display_total(total_qty, subtotal, invalid_count):
    """Print final totals """

    print("\nSales Processing Complete")
    print("-------------------------")
    print(f"Total Items Sold: {total_qty}")
    print(f"Sales Subtotal: ${subtotal:.2f}")
    print(f"Invalid Records: {invalid_count}")
    print("Files Created: sales_summary.csv, errors.log")


def main():
    """Coordinate the program """

    summary, total_qty, subtotal, invalid_count = read_sales()

    save_summary(summary)

    display_total(total_qty, subtotal, invalid_count)


if __name__ == "__main__":
    main()


































































