# KPI Definitions

## Average Order Value (AOV)
AOV reflects how much customers spend per order on average.
Formula:
AOV = SUM(UnitPrice * Quantity * (1 - Discount)) / COUNT(DISTINCT OrderID)

## Gross Margin
This metric estimates profit after accounting for product cost.
Formula:
GM = SUM((UnitPrice - CostOfGoods) * Quantity * (1 - Discount))

Note: Since the dataset doesn’t always include cost details, use a category-level
average or a reasonable approximation when needed.
