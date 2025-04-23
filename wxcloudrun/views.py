from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import pandas as pd
import numpy as np
import joblib

def handle_cats(df):
    df['Sex_Male'] = df['Sex']=='Male'
    df.drop(columns=['Sex'],inplace=True)
    
    df['Diagnostic Name_Lung Cancer'] = df['Diagnostic Name']=='Lung Cancer'
    df['Diagnostic Name_Lung Benign Tumor'] = df['Diagnostic Name']=='Lung Benign Tumor'
    df['Diagnostic Name_Other'] = df['Diagnostic Name']=='Other'
    df.drop(columns=['Diagnostic Name'],inplace=True)
    
    df['Surgical Name_Lobectomy/Radical Resection of Lung Cancer'] = df['Surgical Name']=='Lobectomy/Radical Resection of Lung Cancer'
    df['Surgical Name_Cuneiform Resection'] = df['Surgical Name']=='Cuneiform Resection'
    df['Surgical Name_Segmentectomy'] = df['Surgical Name']=='Segmentectomy'
    df.drop(columns=['Surgical Name'],inplace=True)
    
    df['Surgical Site_Left Lung'] = df['Surgical Site']=='Left Lung'
    df['Surgical Site_Right Lung'] = df['Surgical Site']=='Right Lung'
    df['Surgical Site_Both Lungs'] = df['Surgical Site']=='Both Lungs'
    df.drop(columns=['Surgical Site'],inplace=True)
    
    df['Position_Lobus Superior Pulmonis'] = df['Position']=='Lobus Superior Pulmonis'
    df['Position_Lobi Medii Pulmonis'] = df['Position']=='Lobi Medii Pulmonis'
    df['Position_Lobus Inferior Pulmonis'] = df['Position']=='Lobus Inferior Pulmonis'
    df['Position_Two Lung Lobes'] = df['Position']=='Two Lung Lobes'
    df.drop(columns=['Position'],inplace=True)
    
    print(f'现在的features:{list(df.columns)}')
    return df

def preprocess(data):
    bool_mapping = {
        '否':False,
        '是':True
    }
    new_data = {}
    for k,v in data.items():
        if k == 'age':
            #print(f'正在处理{k}')
            # 检查是否为整数
            try:
                new_data['Age'] = int(data[k])
            except (ValueError, TypeError):
                new_data['Age'] = np.nan
        elif k == 'bmi':
            #print(f'正在处理{k}')
            try:
                new_data['BMI'] = float(data[k])
            except (ValueError, TypeError):
                new_data['BMI'] = np.nan
        elif k == 'height':
            #print(f'正在处理{k}')
            try:
                new_data['Height'] = float(data[k])
            except (ValueError, TypeError):
                new_data['Height'] = np.nan
        elif k == 'weight':
            #print(f'正在处理{k}')
            try:
                new_data['Weight'] = float(data[k])
            except (ValueError, TypeError):
                new_data['Weight'] = np.nan
        elif k == 'gender':
            #print(f'正在处理{k}')
            if v == '男':
                new_data['Sex'] = 'Male'
            else:
                new_data['Sex'] = 'Female'
        elif k == 'fvc':
            try:
                new_data['FVC%'] = float(data[k])
            except (ValueError, TypeError):
                new_data['FVC%'] = np.nan
        elif k == 'fev1':
            try:
                new_data['FEV1%'] = float(data[k])
            except (ValueError, TypeError):
                new_data['FEV1%'] = np.nan
        elif k == 'fev1Fvc':
            try:
                new_data['FEV1/FVC%'] = float(data[k])
            except (ValueError, TypeError):
                new_data['FEV1/FVC%'] = np.nan
        elif k == 'leftVentricularEjectionFraction':
            try:
                new_data['LVEF'] = float(data[k])
            except (ValueError, TypeError):
                new_data['LVEF'] = np.nan          
        elif k == 'diagnosisName':
            #print(f'正在处理{k}')
            diagnosis_mapping = {
                '肺癌': 'Lung Cancer',
                '肺良肿': 'Lung Benign Tumor',
                '其他': 'Other'
            }
            new_data['Diagnostic Name'] = diagnosis_mapping.get(v, 'Other')  # 默认值为 '其他'
        elif k == 'surgeryName':
            #print(f'正在处理{k}')
            surgery_mapping = {
                '肺叶切除术或肺癌根治术': 'Lobectomy/Radical Resection of Lung Cancer',
                '肺楔形切除术': 'Cuneiform Resection',
                '肺段切除术': 'Segmentectomy',
            }
            new_data['Surgical Name'] = surgery_mapping.get(v, 'Cuneiform Resection')
        elif k == 'surgeryPosition':
            #print(f'正在处理{k}')
            surgery_position_mapping = {
                '左肺': 'Left Lung',
                '右肺': 'Right Lung',
                '双肺': 'Both Lungs',
            }
            new_data['Surgical Site'] = surgery_position_mapping.get(v, 'Left Lung')  # 默认值为 '其他'
        elif k=='specificLocation':
            #print(f'正在处理{k}')
            involved_area_mapping = {
                '肺上叶':'Lobus Superior Pulmonis',
                '肺中叶':'Lobi Medii Pulmonis',
                '肺下叶':'Lobus Inferior Pulmonis',
                '两个肺叶':'Two Lung Lobes'
            }
            new_data['Position'] = involved_area_mapping.get(v,'Lobus Superior Pulmonis')
        elif k=='smokingHistory':
            new_data['Smoking History'] = bool_mapping.get(v,0)
        elif k=='hypertension':
            new_data['Hypertension'] = bool_mapping.get(v,0)
        elif k=='diabetes':
            new_data['Diabetes'] = bool_mapping.get(v,0)
        elif k=='postLungSurgery':
            new_data['Post-pulmonary Surgery'] = bool_mapping.get(v,0)
        elif k=='respiratoryDisease':
            new_data['Respiratory Disease'] = bool_mapping.get(v,0)
        elif k=='otherCancer':
            new_data['Other Cancers'] = bool_mapping.get(v,0)
        elif k=='liverKidneyImpairment':
            new_data['Dysfunction of Liver and Kidney'] = bool_mapping.get(v,0)
        elif k=='neurologicalDisease':
            new_data['Nervous System Disease'] = bool_mapping.get(v,0)
        elif k=='asaGrade':
            new_data['ASA'] = bool_mapping.get(v,1)
        elif k=='rcra':
            new_data['RCRI'] = bool_mapping.get(v,1)
    return new_data

def predict(data):
    print(data)
    new_data = preprocess(data)
    new_data = pd.DataFrame([new_data])
    new_data = handle_cats(new_data)
    print(list(new_data.columns))
    cat_cols = joblib.load('./to_app/cat_cols.jbl')

    ##print(list(lgb_features))
    lgb_model = joblib.load('./to_app/lgb_single_model')
    y_pred_lgb = lgb_model.predict_proba(new_data)[:,1]
    print(y_pred_lgb)

    cat_model = joblib.load('./to_app/cat_single_model')
    y_pred_cat = cat_model.predict_proba(new_data)[:,1]
    print(y_pred_cat)

    xgb_model = joblib.load('./to_app/xgb_single_model')
    y_pred_xgb = xgb_model.predict_proba(new_data)[:,1]
    print(y_pred_xgb)

    final_pred = 0.02*y_pred_lgb+0.672*y_pred_cat+0.308*y_pred_xgb
    print(final_pred)
    return final_pred

@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    data = request.get_json()
    print(f'得到的params:{data}')
    pred = predict(data)
    return make_succ_response(data)
    '''
    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')
    '''


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)
