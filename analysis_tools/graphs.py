import matplotlib.pyplot as plt


def simple_graph(list):
    x = [index for index in range(len(list))]
    y = list
    plt.plot(x,y)
    plt.show()

def multi_graph(data, prices, parameters):
    prices_data = [[key, data[key]] for key in prices]
    param_data = [[key, data[key]] for key in parameters]

    x = [ind for ind in range(len(prices_data[0][1]))]
    max_price = []

    
    for list in prices_data:
        y = list[1]
        max_price.append(max(y))

        plt.plot(x,y, label = list[0])
    
    for list in param_data:
        max_ele = max(list[1])/max(max_price)
        y = [ele/max_ele for ele in list[1]]
        plt.plot(x,y, label = list[0])

    plt.legend(loc="lower right")
    plt.show()
