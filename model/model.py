# coding: utf-8

from contextlib import redirect_stdout

import tensorflow as tf
import pandas as pd
import logging
import datetime
import os
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, roc_curve, roc_auc_score

import model.config as config
import model.utils as utils

_logger = logging.getLogger(config.TENSORFLOW_LOGGER_NAME)


def _print_confusion_matrix(confusion_matrix, class_names, figsize = (10,7), fontsize=14):
    
    df_cm = pd.DataFrame(
        confusion_matrix, index=class_names, columns=class_names, 
    )
    fig = plt.figure(figsize=figsize)
    try:
        heatmap = sns.heatmap(df_cm, annot=True, fmt="d")
    except ValueError:
        raise ValueError("Confusion matrix values must be integers.")
    heatmap.yaxis.set_ticklabels(heatmap.yaxis.get_ticklabels(), rotation=0, ha='right', fontsize=fontsize)
    heatmap.xaxis.set_ticklabels(heatmap.xaxis.get_ticklabels(), rotation=45, ha='right', fontsize=fontsize)
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    
    return fig


def data_processing(X_train, Y_train, X_check, Y_check, X_test, Y_test):
    X_train = pd.DataFrame(X_train)
    X_train['label'] = Y_train
    X_check = pd.DataFrame(X_check)
    X_check['label'] = Y_check
    X_test = pd.DataFrame(X_test)
    X_test['label'] = Y_test
    
    return X_train, X_check, X_test


def create_and_save_model(X_train, Y_train, max_seq_length):
    """Create and save the model used by Octav dynamic analysis."""
    _logger.info("Training model...")

    if not os.path.isdir(config.REPOFILES_PATH):
        os.makedirs(config.REPOFILES_PATH)
    
    clf_rf = RandomForestClassifier(n_jobs = -1, oob_score = True, n_estimators = 30)
    clf_rf.fit(X_train['syscall_seq'].values.tolist(), Y_train)
    
    #save model
    with open("files/random_forest_model_{}".format(max_seq_length), 'wb') as f:
        pickle.dump(clf_rf, f)
        _logger.info("Model saved in files/random_forest_model_{}".format(max_seq_length))

    return clf_rf


def check_model(X_train, Y_train, X_check, Y_check, X_test, Y_test, model):
    _logger.info("Assess model and compute metrics...")

    #evaluation
    _logger.info("Score on train dataset : {}".format(model.score(X_train['syscall_seq'].values.tolist(), Y_train)))
    _logger.info("Score on check dataset : {}".format(model.score(X_check['syscall_seq'].values.tolist(), Y_check)))
    _logger.info("Score on test dataset : {}".format(model.score(X_test['syscall_seq'].values.tolist(), Y_test)))
    
    #prediction on check dataset
    preds_rf_check = model.predict_proba(X_check['syscall_seq'].values.tolist())
    X_check['preds_rf_check'] = preds_rf_check[:,1]
    # threshold application
    X_check['preds_label_rf'] = X_check['preds_rf_check'].apply(lambda x : 1 if x > 0.5 else 0)
    #confusion matrix
    confusion_mat_rf_check = confusion_matrix(X_check['label'].values, X_check['preds_label_rf'].values)
    matrix_figure_rf_check = _print_confusion_matrix(confusion_mat_rf_check, ['Benign', 'Malicious'])
    matrix_figure_rf_check.savefig("model_assessment/confusion_matrix_check")
    _logger.info("Confusion matrix on check dataset saved in model_assessment/confusion_matrix_check")
    
    #ROC curve
    fpr, tpr, threshold = roc_curve(X_check['label'], X_check['preds_rf_check'])
    auc_rf = roc_auc_score(X_check['label'], X_check['preds_rf_check'])
    
    roc_curve_check = plt.figure()
    plt.title('ROC Curves')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.plot(fpr, tpr, label='RF auc :'+str(auc_rf))
    plt.legend(loc=4)
    roc_curve_check.savefig("model_assessment/roc_curve_check")
    _logger.info("ROC curve on check dataset saved in model_assessment/roc_curve_check")
    
    #prediction on test dataset
    preds_rf_test = model.predict_proba(X_test['syscall_seq'].values.tolist())
    X_test['preds_rf_test'] = preds_rf_test[:,1]
    # threshold application
    X_test['preds_label_rf'] = X_test['preds_rf_test'].apply(lambda x : 1 if x > 0.5 else 0)
    #confusion matrix
    confusion_mat_rf_test = confusion_matrix(X_test['label'].values, X_test['preds_label_rf'].values)
    matrix_figure_rf_test = _print_confusion_matrix(confusion_mat_rf_test, ['Benign', 'Malicious'])
    matrix_figure_rf_test.savefig("model_assessment/confusion_matrix_test")
    _logger.info("Confusion matrix on test dataset saved in model_assessment/confusion_matrix_test")
    
    #ROC curve
    fpr, tpr, threshold = roc_curve(X_test['label'], X_test['preds_rf_test'])
    auc_rf = roc_auc_score(X_test['label'], X_test['preds_rf_test'])
    
    roc_curve_test = plt.figure()
    plt.title('ROC Curves')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.plot(fpr, tpr, label='RF auc :'+str(auc_rf))
    plt.legend(loc=4)
    roc_curve_test.savefig("model_assessment/roc_curve_test")
    _logger.info("ROC curve on test dataset saved in model_assessment/roc_curve_test")