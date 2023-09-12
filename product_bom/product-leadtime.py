import pandas

def get_cumulative_leadtime(lt_df:pandas.DataFrame,bom_df:pandas.DataFrame,product:str,path:list[str]):
    max_child_lt = 0
    max_child_path = []
    for child in bom_df[bom_df['Parent'] == product]['Child']:
        child_path=[]
        child_lt = get_cumulative_leadtime(lt_df,bom_df,child,child_path)
        if child_lt > max_child_lt:
            max_child_lt = child_lt
            max_child_path = child_path

    total = get_lt(lt_df,product) + max_child_lt
    path.append(product)
    path.extend(max_child_path)
    return total

def get_lt(lt_df:pandas.DataFrame,product:str):
    lt = lt_df.loc[product]['Leadtime']
    return lt

def main():
    lt_df = pandas.read_csv('lt.txt')
    lt_df.set_index(keys='Product',drop=False,inplace=True)
    bom_df = pandas.read_csv('bom.txt')

    top_product = 'A'
    path = []
    lt = get_cumulative_leadtime(lt_df,bom_df,top_product,path)
    print(f"for product {top_product} the lead time is {lt} the path is {path}")


if __name__ == '__main__':  
    main()