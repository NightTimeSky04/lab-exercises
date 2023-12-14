import gurobipy as gp
from gurobipy import GRB
import numpy as np


def optimise_production(available_time_h, available_starting_cash_USD):
    try:
        model = gp.Model("production")

        products = model.addMVar(shape=2, vtype=GRB.INTEGER, name="product")

        # Time and cash constraints
        max_costs = np.array([available_time_h, available_starting_cash_USD])

        time_costs_hpu = np.array([3.0, 4.0])

        cash_costs_USDpu = np.array([3.0, 2.0])
        revenues_USDpu = np.array([6.0, 5.4])
        cash_from_revenue_ratios = np.array([[0.45, 0.0], [0.0, 0.3]])
        eff_cash_costs_USDpu = cash_costs_USDpu - \
            cash_from_revenue_ratios @ revenues_USDpu

        costs = np.array([time_costs_hpu, eff_cash_costs_USDpu])

        model.addConstr(costs @ products <= max_costs, name="constraint")

        # Non-negativity constraints
        model.addConstr(products >= np.array([0, 0]), "non-negativity")

        # Objective function
        profit = revenues_USDpu - cash_costs_USDpu - \
            (cash_from_revenue_ratios @ revenues_USDpu)
        model.setObjective(profit @ products, GRB.MAXIMIZE)

        model.optimize()

        print("\nUnits to produce")
        count1, count2 = products.X
        print("Product 1: %s" % abs(int(count1)))
        print("Product 2: %s" % abs(int(count2)))

        # Check constraints hold
        assert (eff_cash_costs_USDpu @ products.X <=
                available_starting_cash_USD)
        assert (time_costs_hpu @ products.X <= available_time_h)

        # Check for excess time or cash
        cash_remainder = available_starting_cash_USD - \
            (eff_cash_costs_USDpu @ products.X)
        time_remainder = available_time_h - (time_costs_hpu @ products.X)
        assert ((time_remainder <= min(time_costs_hpu))
                or (cash_remainder <= min(cash_costs_USDpu)))

        total_profit = model.ObjVal
        print("\nTotal profit: $%.2f" % total_profit)

        return total_profit

    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ': ' + str(e))

    except AttributeError:
        print('Encountered an attribute error')


print("\n\n Part a:\n----------\n")
A = optimise_production(20_000, 4000)

print("\n\n Part b:\n----------\n")
B = optimise_production(22_000, 3600)

if B <= A:
    print("\nInvesting some starting cash does not improve profit margin.")
else:
    print("\nInvesting some starting cash improves profit margin by $%.2f." % (B - A))
