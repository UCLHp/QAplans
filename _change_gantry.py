import pydicom
import easygui as eg


def change_gantry():
    '''Function to change the Treatment room tag for all beams in a dicom plan
    '''
    # Select file to be changed
    my_path = eg.fileopenbox('Select plan file(s) to be changed', multiple=True)
    if not isinstance(my_path, list):
        list(my_path)

        gantry = eg.choicebox('Room selection',
                              'Select desired Gantry',
                              ['Gantry 1', 'Gantry 2', 'Gantry 3', 'Gantry 4']
                              )

     for fl in my_path:
        my_dcm = pydicom.dcmread(fl)

        # print(f'Number of fields: {len(my_dcm.IonBeamSequence)}\n')

        count = 1
        for field in my_dcm.IonBeamSequence:
            # print(f'Field {count} is currently {field.TreatmentMachineName}')
            field.TreatmentMachineName = gantry
            # print(f'Field {count} changed to {field.TreatmentMachineName}\n')

        # print('All fields changed\n')

        # print('Overwriting File\n')
        my_dcm.save_as(fl)
        # print('File Saved')


if __name__ == '__main__':
    change_gantry()
