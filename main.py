

huePercent = 0

# MAIN LOOP
# Continuously read and print packets
while True:
    try:
        # if masterList['']
        # hueNow += 5
        # if hueNow > 255:
        #     hueNow -= 255
        # print hueNow

        # NEED TO BUILD INTO PROPER MODEL LOGIC STRUCTURE
        # Put broadcast data into structure and send out to units
        # 
        # print "hue ", hueNow
        time.sleep(0.1)

        huePercent+=0.05
        if huePercent > 1:
            huePercent = 0
        broadcastData = { "pName" : "hue", "per" : huePercent }
        sendBroadcast( xbee, broadcastData )
        print "after broadcast"
        print broadcastData

    except KeyboardInterrupt:
        print "KeyboardInterrupt EXCEPT"
        break
    except:
        print "Generic EXCEPT"
        break