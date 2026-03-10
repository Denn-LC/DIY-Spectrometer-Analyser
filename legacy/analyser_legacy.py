import cv2
import numpy as np
import matplotlib.pyplot as plt


def main():
    cap = cv2.VideoCapture(0)

    roi_selected = False
    
    while(True):
        ret, frame = cap.read()
        
        k = cv2.waitKey(1)
        
        if k & 0xFF == ord('s') and roi_selected == True:
            shape = cropped.shape
            r_dist = []
            b_dist = []
            g_dist = []
            i_dist = []
            for i in range(shape[1]):
                b_val = np.mean(cropped[:, i][:, 0])  # index 0 = Blue
                g_val = np.mean(cropped[:, i][:, 1])  # index 1 = Green
                r_val = np.mean(cropped[:, i][:, 2])  # index 2 = Red
                i_val = (r_val + b_val + g_val) / 3

                r_dist.append(r_val)
                g_dist.append(g_val)
                b_dist.append(b_val)
                i_dist.append(i_val)

            # Display cropped image on top
            plt.subplot(2, 1, 1)
            cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB for display
            plt.imshow(cropped_rgb)
            plt.title('Selected ROI')
            plt.axis('off')
            
            plt.subplot(2, 1, 2)
            plt.plot(r_dist, color='r', label='red')      
            plt.plot(g_dist, color='g', label='green')
            plt.plot(b_dist, color='b', label='blue')
            plt.plot(i_dist, color='k', label='mean')
            plt.xlabel('Pixel Position')
            plt.ylabel('Intensity')
            plt.title('Spectrum Analysis')
            plt.legend(loc="upper left")
            plt.show()

        elif k & 0xFF == ord('r'):
            r = cv2.selectROI(frame)
            roi_selected = True
            
        elif k & 0xFF == ord('q'):
            break
        
        else:
            if roi_selected:
                cropped = frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
                cv2.imshow('roi', cropped)
            else:
                cv2.imshow('frame', frame)
        
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()