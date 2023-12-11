from falkner_skan import falkner_skan
import numpy as np
import csv

#data management
fileName = ('example.csv') #put the name of your file here
data_delimiter = ';'
rows = []
new_rows = []

#reads the file with the xflr5 data
with open(fileName, 'r', newline='') as f:
    reader = csv.reader(f, delimiter= data_delimiter)

    row1 = next(reader) #header is saved and skipped

    for line in reader: #saves the rows of the document in a list
        rows.append(line)


#conditions
kin_visc = 1.54e-5 #kinetic viscosity in m^2/s
c_length = 0.14 #chord length in meter


#m value testing algorithm settings
depth = 50 #depth of the algorithm/iterations to narrow down to the m
samplesPerDepth = 4 #number of samples the algorithm will split the intervals in to search for m


def getDeltaStar(eta, f1): #function to calculate the displacement thickness
    DeltaStar = np.trapz(
    (1 - f1),
    dx=eta[1]
    )
    print(f"DeltaStar: {DeltaStar}")
    return DeltaStar


def getTheta(eta, f1): #function to calculate the momentum thickness
    Theta = np.trapz(
        f1 * (1 - f1),
        dx=eta[1]
    )
    print(f"Theta: {Theta}")
    return Theta


def calculate_g(Theta, XFLR_Theta): #function to calculate the transformation function "g"
    g = Theta / XFLR_Theta
    print(f"g: {g}")
    return g


def calculate_Re_k(calc_m): #function to calculate the Re_k resulting of the values given by the data file
    eta, f0, f1, f2 = falkner_skan(m=calc_m) #calls to solve falkner skan equation
    theta = getTheta(eta, f1)
    g_calc = calculate_g(theta, xflr_theta)
    calc_eta = g_calc * trip_thickness
    print(f"Berechnetes Eta: {calc_eta}")
    f1_at_calc_eta = np.interp(calc_eta,eta, f1)
    print(f"f1 at calc_eta: {f1_at_calc_eta}")
    Uk_Ue_ratio = f1_at_calc_eta
    print(f"Uk_Ue_ratio: {Uk_Ue_ratio}")
    Ue_calc = xflr_Ue * U_inf
    U_k_calc = Uk_Ue_ratio * Ue_calc
    Re_k_calc = (U_k_calc * trip_thickness * c_length) / kin_visc
    print(f"Re_k: {Re_k_calc}")
    return Re_k_calc


def get_shapefactor(m_val): #calculates the shapefactor from the determined m
    eta, f0, f1, f2 = falkner_skan(m=m_val)
    print(f"current m: {m_val}")
    deltaStar = getDeltaStar(eta, f1)
    theta = getTheta(eta, f1)
    shapeFactor = deltaStar / theta
    print(f"ShapeFactor: {shapeFactor}")
    return shapeFactor

#algorithm to find the fitting m to the given shapefactor (XFLR5's)
for line in rows:
    #setting starting conditions of the algorithm
    interval = [-0.09, 2.0] #interval in which m is searched
    intervalOrig = interval
    mOfInterest = interval[0]
    sampleIntervalStart = interval[0]

    #set all the values from the xflr5 data
    trip_thickness_measured = float(line[0])
    trip_thickness = trip_thickness_measured / (c_length * 1000)
    Re = int(line[1])
    U_inf = (Re * kin_visc) / c_length
    alpha = float(line[2])
    xflr_H12 = float(line[3])
    xflr_theta = float(line[4])
    xflr_Ue = float(line[5])

    #narrow down m
    for accuracy in range(depth):
        intervalSize = interval[1] - interval[0]

        for sample in range(samplesPerDepth + 1): #sort the samples that are smaller than the desired m in one list, and the bigger ones in another
            list_smaller = [interval[0]]
            list_bigger = [interval[1]]
            currentSample = sampleIntervalStart + sample * (intervalSize / float(samplesPerDepth))
            calc_ShapeFactor = get_shapefactor(currentSample)

            if calc_ShapeFactor > xflr_H12:
                list_smaller.append(currentSample)
                list_smaller.sort()
            else:
                list_bigger.append(currentSample)
                list_bigger.sort()

            # the correct m must be between the smallest value of the "bigger list" and the biggest of the "smaller list"
            interval = [list_smaller[-1], list_bigger[0]]   #sets the new interval accordingly
            print(f"Interval: {interval}")
            sampleIntervalStart = interval[0]
            mOfInterest = (interval[0] + interval[1])/2 #the m is set to the middle of the interval; that's the best m for that iteration

    print("closest m: ", mOfInterest)
    print(f"ShapeFactor after m test: {get_shapefactor(mOfInterest)}")

    Re_k = calculate_Re_k(mOfInterest) #calculates the Re_k after it found the closest m

    new_line = [trip_thickness_measured, Re, alpha, xflr_H12, xflr_theta, xflr_Ue, Re_k, mOfInterest] #also saves mOfInterest for testing purposes
    new_rows.append(new_line) #appends the data with Re_k into the row

#writes the new data into the file
with open(fileName, 'w', newline='') as f:
    writer = csv.writer(f, delimiter= data_delimiter)

    writer.writerow(row1)
    writer.writerows(new_rows)

print(f"Data saved!")


