import jsonpath


def payload(input_data):
    if isinstance(input_data, str):
        input_data = eval(input_data)

    for k, v in input_data.get('params').items():
        s = str(input_data.get('expr'))
        m = s.replace(jsonpath.jsonpath(input_data.get('expr'), k)[0], v)
        input_data['expr'] = eval(m)
    print(input_data)
    return input_data


if __name__ == '__main__':
    input_data = {
        "params": {
            "request.body.page": "XXX",
            "request.body.row": "YYY",
        },
        "expr": {
            "request": {
                "body": {
                    "page": "params[request.body.page]",
                    "row": '6'
                },
                "header": {
                    "device": {
                        "model": "SM-N7508V",
                        "osVersion": "4.3",
                        "imei": "352203064891579",
                        "isRoot": "1",
                        "nfc": "1",
                        "brand": "samsung",
                        "mac": "B8:5A:73:94:8F:E6",
                        "uuid": "45cnqzgwplsduran7ib8fw3aa",
                        "osType": "01"
                    },
                    "appId": "1",
                    "net": {
                        "ssid": "oa-wlan",
                        "netType": "WIFI_oa-wlan",
                        "cid": "17129544",
                        "lac": "41043",
                        "isp": "",
                        "ip": "195.214.145.199"
                    },
                    "appVersion": "3.60",
                    "transId": "Financialpage",
                    "reqSeq": "0"
                }
            }
        }
    }

    payload(input_data)
