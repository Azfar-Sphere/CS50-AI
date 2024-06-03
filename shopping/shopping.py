import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []
    with open(filename, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            d_e = []
            d_l = []
            
            d_e.append(int(row["Administrative"]))
            d_e.append(float(row["Administrative_Duration"]))
            d_e.append(int(row["Informational"]))
            d_e.append(float(row["Informational_Duration"]))
            d_e.append(int(row["ProductRelated"]))
            d_e.append(float(row["ProductRelated_Duration"]))
            d_e.append(float(row["BounceRates"]))
            d_e.append(float(row["ExitRates"]))
            d_e.append(float(row["PageValues"]))
            d_e.append(float(row["SpecialDay"]))
            d_e.append(month(row["Month"]))
            d_e.append(int(row["OperatingSystems"]))
            d_e.append(int(row["Browser"]))
            d_e.append(int(row["Region"]))
            d_e.append(int(row["TrafficType"]))

            visitortype = row["VisitorType"]
            if visitortype == "Returning_Visitor":
                d_e.append(1)
            else:
                d_e.append(0)

            weekend = row["Weekend"]
            if weekend == "TRUE":
                d_e.append(1)
            else:
                d_e.append(0)

            label = row["Revenue"]
            if label == "TRUE":
                d_l.append(1)
            else:
                d_l.append(0)
            
            evidence.append(d_e)
            labels.append(d_l)

    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)

    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    senstivity = 0
    specificity = 0
    
    p_count = 0
    n_count = 0

    for label in labels:
        label = int(label)
        if label:
            p_count += 1
        
        else:
            n_count += 1

    p_correct = 0
    n_correct = 0
        
    for i in range(len(labels)):
        if labels[i] == predictions[i]:
            label = int(labels[i])
            if label:
                p_correct += 1
            else:
                n_correct += 1
    
    senstivity = float(p_correct / p_count)
    specificity = float(n_correct / n_count)

    return (senstivity, specificity)


def month(month):
    match month:
        case "Jan":
            return 0
        case "Feb":
            return 1
        case "Mar":
            return 2
        case "Apr":
            return 3
        case "May":
            return 4
        case "Jun":
            return 5
        case "Jul":
            return 6
        case "Aug":
            return 7
        case "Sep":
            return 8
        case "Oct":
            return 9
        case "Nov":
            return 10
        case "Dec":
            return 11


if __name__ == "__main__":
    main()
