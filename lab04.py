
import os

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------
# Question # 1
# ---------------------------------------------------------------------


def latest_login(login):
    """Calculates the latest login time for each user
    :param login: a dataframe with login information
    :return: a dataframe with latest login time for
    each user indexed by "Login Id"
    >>> fp = os.path.join('data', 'login_table.csv')
    >>> login = pd.read_csv(fp)
    >>> result = latest_login(login)
    >>> len(result)
    433
    >>> result.loc[381, "Time"].hour > 12
    True
    """
    df  = login
    df = df.groupby("Login Id").max()
    df["Time"] = pd.to_datetime(df["Time"])

    

    return df

# ---------------------------------------------------------------------
# Question # 2
# ---------------------------------------------------------------------


def smallest_ellapsed(login):
    """
    Calculates the the smallest time elapsed for each user.
    :param login: a dataframe with login information but without unique IDs
    :return: a dataframe, indexed by Login ID, containing 
    the smallest time elapsed for each user.
    >>> fp = os.path.join('data', 'login_table.csv')
    >>> login = pd.read_csv(fp)
    >>> result = smallest_ellapsed(login)
    >>> len(result)
    238
    >>> 18 < result.loc[1233, "Time"].days < 23
    True
    """
    df = login
    df["Time"] = pd.to_datetime(df["Time"])


    return df.groupby("Login Id").agg(lambda group: group.diff().min()).dropna()["Time"].to_frame()


# ---------------------------------------------------------------------
# Question # 3
# ---------------------------------------------------------------------


def total_seller(df):
    """
    Total for each seller
    :param df: like sales
    :return: pivot table
    >>> fp = os.path.join('data', 'sales.csv')
    >>> df = pd.read_csv(fp)
    >>> out = total_seller(df)
    >>> out.index.dtype
    dtype('O')
    >>> out["Total"].sum() < 15000
    True

    """
    
    return pd.pivot_table(df, values = "Total", index = ["Name"], aggfunc = "sum")


def product_name(df):
    """
    :param df: like sales
    :return: pivot table
    >>> fp = os.path.join('data', 'sales.csv')
    >>> df = pd.read_csv(fp)
    >>> out = product_name(df)
    >>> out.size
    15
    >>> out.loc["pen"].isnull().sum()
    0
    """
    
    return pd.pivot_table(df, values = "Total", index = ["Product"], columns = ["Name"] ,aggfunc =
                          {"Total": np.sum})


def count_product(df):
    """
    :param df: like sales
    :return: pivot table
    >>> fp = os.path.join('data', 'sales.csv')
    >>> df = pd.read_csv(fp)
    >>> out = count_product(df)
    >>> out.loc["boat"].loc["Trump"].value_counts()[0]
    6
    >>> out.size
    70
    """
   
    return pd.pivot_table(df, values = "Total", index = ["Product", "Name"], columns = ["Date"] ,
                          aggfunc = {"Total": {"Total" : "sum"}}).fillna(0)


def total_by_month(df):
    """
    :param df: like sales
    :return: pivot table
    >>> fp = os.path.join('data', 'sales.csv')
    >>> df = pd.read_csv(fp)
    >>> out = total_by_month(df)
    >>> out["Total"]["May"].idxmax()
    ('Smith', 'book')
    >>> out.shape[1]
    5
    """
    
    df["Month"] = df["Date"].str.split(".").apply(lambda x: x[0])
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    month_values = ["January", "Feburary", "March",
                   "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    month_dict = dict(zip(months, month_values))
    df =df.replace({"Month":month_dict})
    
    
    return pd.pivot_table(df, index = ["Name", "Product"], columns = ["Month"] ,aggfunc = {"Total": "sum"}).fillna(0)

# ---------------------------------------------------------------------
# Question # 4
# ---------------------------------------------------------------------


def diff_of_means(data, col='orange'):
    """
    diff_of_means takes in a dataframe of counts 
    of skittles (like skittles) and their origin 
    and returns the absolute difference of means 
    between the number of oranges per bag from Yorkville and Waco.

    :Example:
    >>> skittles_fp = os.path.join('data', 'skittles.tsv')
    >>> skittles = pd.read_csv(skittles_fp, sep='\\t')
    >>> out = diff_of_means(skittles)
    >>> 0 <= out
    True
    """
    skittles = data
    skittles["sum"] = skittles.sum(numeric_only=True, axis=1)
    yorkville = skittles.loc[skittles["Factory"] == "Yorkville"]
    waco = skittles.loc[skittles["Factory"] == "Waco"]
    
    return abs(yorkville[col].mean() -waco[col].mean())


def simulate_null(data, col='orange'):
    """
    simulate_null takes in a dataframe of counts of 
    skittles (like skittles) and their origin, and 
    generates one instance of the test-statistic 
    under the null hypothesis

    :Example:
    >>> skittles_fp = os.path.join('data', 'skittles.tsv')
    >>> skittles = pd.read_csv(skittles_fp, sep='\\t')
    >>> out = simulate_null(skittles)
    >>> isinstance(out, float)
    True
    >>> 0 <= out <= 1.0
    True
    """
    df = data.loc[data["Factory"].isin(np.array(["Waco", "Yorkville"]))]
    df = df[[col, "Factory"]]
    shuffled= (
        df[col]
        .sample(replace=False, frac=1)
        .reset_index(drop=True)
    )

    original_and_shuffled = (
        df
        .assign(**{'Shuffled Orange Amount': shuffled})
    )
    
    return abs(original_and_shuffled.groupby('Factory')["Shuffled Orange Amount"].mean().diff()[1])


def pval_orange(data, col='orange'):
    """
    pval_orange takes in a dataframe of counts of 
    skittles (like skittles) and their origin, and 
    calculates the p-value for the permutation test 
    using 1000 trials.
    
    :Example:
    >>> skittles_fp = os.path.join('data', 'skittles.tsv')
    >>> skittles = pd.read_csv(skittles_fp, sep='\\t')
    >>> pval = pval_orange(skittles)
    >>> isinstance(pval, float)
    True
    >>> 0 <= pval <= 0.1
    True
    """
    n_trials = 1000
    differences = []
    observed_difference = diff_of_means(data, col)
    for _ in range(n_trials):

        # shuffle the weights
        difference = simulate_null(data, col)


        # add it to the list of results
        differences.append(difference)
    
    
    return np.count_nonzero(differences >= observed_difference) / n_trials


# ---------------------------------------------------------------------
# Question # 5
# ---------------------------------------------------------------------

def ordered_colors():
    """
    ordered_colors returns your answer as an ordered
    list from "most different" to "least different" 
    between the two locations. You list should be a 
    hard-coded list, where each element has the 
    form (color, p-value).

    :Example:
    >>> out = ordered_colors()
    >>> len(out) == 5
    True
    >>> colors = {'green', 'orange', 'purple', 'red', 'yellow'}
    >>> set([x[0] for x in out]) == colors
    True
    >>> all([isinstance(x[1], float) for x in out])
    True
    """

    return [("yellow",0.263) ,("orange", 0.047), ("red",0.0),("green", 0.444), ("purple", 0.972)]
    

# ---------------------------------------------------------------------
# Question # 6
# ---------------------------------------------------------------------

def same_color_distribution():
    """
    same_color_distribution outputs a hard-coded tuple 
    with the p-value and whether you 'Accept' or 'Reject' 
    the null hypothesis.

    >>> out = same_color_distribution()
    >>> isinstance(out[0], float)
    True
    >>> out[1] in ['Fail to Reject', 'Reject']
    True
    """
    
    
    return 0.03, "Fail to Reject"

# ---------------------------------------------------------------------
# Question # 7
# ---------------------------------------------------------------------

def perm_vs_hyp():
    """
    Multiple choice response for question 8

    >>> out = perm_vs_hyp()
    >>> ans = ['P', 'H']
    >>> len(out) == 5
    True
    >>> set(out) <= set(ans)
    True
    """

    return ["P","P","P","P","P"]


# ---------------------------------------------------------------------
# Question # 8
# ---------------------------------------------------------------------

def after_purchase():
    """
    Multiple choice response for question 8

    >>> out = after_purchase()
    >>> ans = ['MD', 'MCAR', 'MAR', 'NI']
    >>> len(out) == 5
    True
    >>> set(out) <= set(ans)
    True
    """

    return ["MCAR", "MD", "NI", "MAR","MAR"]

# ---------------------------------------------------------------------
# Question # 9
# ---------------------------------------------------------------------


def multiple_choice():
    """
    Multiple choice response for question 9

    >>> out = multiple_choice()
    >>> ans = ['MD', 'MCAR', 'MAR', 'NI']
    >>> len(out) == 5
    True
    >>> set(out) <= set(ans)
    True
    >>> out[1] in ans
    True
    """

    return ["MAR", "MAR", "NI", "NI", "MCAR"]

# ---------------------------------------------------------------------
# DO NOT TOUCH BELOW THIS LINE
# IT'S FOR YOUR OWN BENEFIT!
# ---------------------------------------------------------------------


# Graded functions names! DO NOT CHANGE!
# This dictionary provides your doctests with
# a check that all of the questions being graded
# exist in your code!

GRADED_FUNCTIONS = {
    'q01': ['latest_login'],
    'q02': ['smallest_ellapsed'],
    'q03': ['total_seller', 'product_name', 'count_product', 'total_by_month'],
    'q04': ['diff_of_means', 'simulate_null', 'pval_orange'],
    'q05': ['ordered_colors'],
    'q06': ['same_color_distribution'],
    'q07': ['perm_vs_hyp'],
    'q08': ['after_purchase'],
    'q09': ['multiple_choice']
}


def check_for_graded_elements():
    """
    >>> check_for_graded_elements()
    True
    """
    
    for q, elts in GRADED_FUNCTIONS.items():
        for elt in elts:
            if elt not in globals():
                stmt = "YOU CHANGED A QUESTION THAT SHOULDN'T CHANGE! \
                In %s, part %s is missing" % (q, elt)
                raise Exception(stmt)

    return True
