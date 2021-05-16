from flask import Flask, request
from flask import jsonify
from utilities.db_utils import make_connection, execute_query

app = Flask(__name__)


# http://0.0.0.0:5353/api/v1/?groupby=channel,country,date&sortby=impressions=asc&filterby=date_from=2020-01-01,date_to=2020-05-16,channel=adcolony,country=us,os=android&derived=cpi


def get_param_values(values):
    """
    A function to convert url params to dictionary
    :param values: a string input with multiple key and values split by comma
    :return: a dictionary of key and values present on input
    """
    mapping = {}
    values = values.split(',')
    for value in values:
        key, val = value.split('=')
        mapping[key] = val
    return mapping


def validate_options(accepted_options, actual_options):
    """
    A function to validate the url params passed
    :param accepted_options:  A list of acceptable options
    :param actual_options: A list of actual options present in URL
    :return: a boolean value
    """
    ret_val = True
    for option in actual_options:
        if option not in accepted_options:
            ret_val = False
    return ret_val


def construct_query(group_options, filter_options, order_options, derived_options, aggregate_options, select_options):
    """
    A function to construct the query based on various filters, grouping,aggregate functions and sorting passed through url params

    :param group_options: list of column names using which result is to be grouped
    :param filter_options: A dictionary containing conditions for where clause
    :param order_options: A dictionary containing columns names as key and Asc or Desc as values, for sorting final output
    :param derived_options: A list denoting all derived columns
    :param aggregate_options: A string containing values such as sum,min,max
    :param select_options: A list of columns which are to be chosen, other than group by columns
    :return: A query as string and list of columns in output
    """

    selected_columns = []

    query_string = "select "

    # constructing the columns to be selected with aggregate functions

    for option in group_options:
        query_string += option + ', '
        selected_columns.append(option)

    columns = ['impressions', 'clicks', 'installs', 'spend', 'revenue']
    use_columns = select_options
    if len(select_options) == 0:
        use_columns = columns

    for i, option in enumerate(use_columns):
        query_string += f'{aggregate_options}({option}) as {option}'
        selected_columns.append(f'{option}')
        if i < len(use_columns) - 1:
            query_string += ', '

    for i, option in enumerate(derived_options):
        if option == 'cpi':
            query_string += ',sum(spend)/sum(installs) as cpi '
            selected_columns.append('cpi')

    # Adding database to the constructed query
    query_string += ' from dataset where '

    # Adding filter options to query
    for i, option in enumerate(sorted(filter_options.keys())):
        if option == 'date_from':
            query_string += f' day >= date(\'{filter_options["date_from"]}\')'
        elif option == 'date_to':
            query_string += f' day <= date(\'{filter_options["date_to"]}\')'
        elif option == 'date_eq':
            query_string += f' day = date(\'{filter_options["date_eq"]}\')'
        elif option == 'date_gt':
            query_string += f' day > date(\'{filter_options["date_gt"]}\')'
        elif option == 'date_gte':
            query_string += f' day >= date(\'{filter_options["date_gte"]}\')'
        elif option == 'date_lt':
            query_string += f' day < date(\'{filter_options["date_lt"]}\')'
        elif option == 'date_lte':
            query_string += f' day <= date(\'{filter_options["date_lte"]}\')'
        else:
            query_string += f' lower({option}) = lower("{filter_options[option]}")'


        if i < len(filter_options) - 1:
            query_string += ' and '
        else:
            query_string += ' '

    # Adding group by to constructed query
    query_string += 'group by '
    for i, option in enumerate(group_options):
        query_string += option
        if i < len(group_options) - 1:
            query_string += ' ,'

    # Adding order by to constructed query
    query_string += ' order by '
    for i, option in enumerate(order_options):
        query_string += f'{option} {order_options[option]} '
        if i < len(order_options) - 1:
            query_string += ' , '

    return query_string, selected_columns


@app.route("/api/v1/query/", methods=['GET'])
def index():
    accepted_filter_options = ['date_gt','date_gte','date_lt','date_lte', 'date_to', 'date_eq', 'channel', 'country', 'os']
    accepted_groupby_options = ['day', 'channel', 'country', 'os']
    accepted_derived_metric = ['cpi']
    accepted_sortby_options = ['day', 'channel', 'country', 'os', 'impressions', 'clicks', 'installs', 'spend',
                               'revenue', 'cpi']
    accepted_aggregate_options = ['sum', 'max', 'min']
    acccepted_select_options = ['impressions', 'clicks', 'installs', 'spend', 'revenue']

    filter_options = get_param_values(request.args.get('filterby'))

    groupby_options = []
    if request.args.get('groupby'):
        groupby_options = request.args.get('groupby').split(',')

    select_options = []
    if request.args.get('select'):
        select_options = request.args.get('select').split(',')

    derived_options = []
    if request.args.get('derived'):
        derived_options = request.args.get('derived').split(',')

    aggregate_options = None
    if request.args.get('aggregate'):
        aggregate_options = request.args.get('aggregate')

    sortby_options = get_param_values(request.args.get('sortby'))

    if not validate_options(accepted_options=accepted_filter_options, actual_options=filter_options.keys()):
        return jsonify({'error': f'Got an unexpected filterby option. Accepted options are {accepted_filter_options}',
                        'success': False})

    if not validate_options(accepted_options=accepted_groupby_options, actual_options=groupby_options):
        return jsonify({'error': f'Got an unexpected groupby option. Accepted options are {accepted_groupby_options}',
                        'success': False})

    if not validate_options(accepted_options=accepted_derived_metric, actual_options=derived_options):
        return jsonify({'error': f'Got an unexpected derived option. Accepted options are {accepted_derived_metric}',
                        'success': False})

    if not validate_options(accepted_options=accepted_sortby_options, actual_options=sortby_options):
        return jsonify({'error': f'Got an unexpected orderby option. Accepted options are {accepted_sortby_options}',
                        'success': False})

    if not validate_options(accepted_options=accepted_aggregate_options, actual_options=[aggregate_options]):
        return jsonify(
            {'error': f'Got an unexpected aggregate option. Accepted options are {accepted_aggregate_options}',
             'success': False})

    if not validate_options(accepted_options=acccepted_select_options, actual_options=select_options):
        return jsonify({'error': f'Got an unexpected select option. Accepted options are {acccepted_select_options}',
                        'success': False})

    query_string, columns = construct_query(group_options=groupby_options, filter_options=filter_options,
                                            order_options=sortby_options, \
                                            derived_options=derived_options, aggregate_options=aggregate_options,
                                            select_options=select_options)
    app.logger.info(f'Executing Query')
    app.logger.info(f'{query_string}')
    app.logger.info(f'Columns selected {columns}')

    status,results = execute_query(query_string, columns)

    if not status:
        return jsonify({'success':False, 'error': results})

    return jsonify({'success':True,'data':results})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5353)
