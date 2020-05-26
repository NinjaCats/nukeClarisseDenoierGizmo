import nuke
import os
import threading
import sys


class Denoiser(threading.Thread):
    def __init__(self, threadID, srcfile, outfile, strength=1, usealbedo=0, albedo="", usenormal=0, normal=""):
        super(Denoiser, self).__init__()
        self.srcfile = srcfile
        self.outfile = outfile
        self.strength = strength
        self.usealbedo = usealbedo
        self.albedo = albedo
        self.usenormal = usenormal
        self.normal = normal
        self.threadID = threadID

    def run(self):
        print "Denoiser Current thread id %s" % self.threadID
        print "-" * 20
        Denoiser.denoiser(self.srcfile, self.outfile, self.strength, self.usealbedo,
                          self.albedo, self.usenormal, self.normal)

    @staticmethod
    def denoiser(srcfile, outfile, strength, usealbedo=0, albedo="", usenormal=0, normal=""):
        if usealbedo:
            cmd = "cdenoise.exe %s -strength %s -albedo %s -output %s" % (
                srcfile, strength, albedo, outfile)
        elif usenormal:
            cmd = "cdenoise.exe %s -strength %s -albedo %s -world_normal %s -output %s" % (
                srcfile, strength, albedo, normal, outfile)
        else:
            cmd = "cdenoise.exe %s -strength %s -output %s" % (
                srcfile,  outfile)
        return os.system(cmd)


if __name__ == "__main__":
    node = nuke.thisNode()
    imageNode = nuke.thisGroup().input(0)
    iamgeRange = int(imageNode["last"].getValue())
    imageFile = imageNode["file"].getValue()

    imageFiles = []

    getStrength = node["strength"].getValue()

    sys.path.append(node["clarisseRoot"].getValue())

    print "prograss in Set Channel"

    useAlbedo = int(node["useAlbedo"].getValue())
    useNormal = int(node["useNormal"].getValue())
    channelAlbedoNum = int(node["albedo"].getValue())
    channelAlbedo = node["albedo"].enumName(channelAlbedoNum)
    channelNormalNum = int(node["normal"].getValue())
    channelNormal = node["normal"].enumName(channelAlbedoNum)

    print "prograss in Set File"

    try:
        imageFiles = [imageFile % int(f + 1) for f in range(iamgeRange)]
    except TypeError as e:
        print "Single File"
        imageFiles.append(imageFile)

    def out(x): return os.path.join(*x)
    def getName(x): return os.path.split(x)[-1]

    outDir = node["outDir"].getValue()
    outFiles = [out((outDir, getName(f))) for f in imageFiles]

    print imageFiles
    print "prograss in Exturde"

    if not node["threads"].getValue():
        print "prograss in No thread"
        for i in range(len(imageFiles)):
            Denoiser.denoiser(
                imageFiles[i], outFiles[i], getStrength, useAlbedo, channelAlbedo, useNormal, channelNormal)
    else:
        print "prograss in Mutli-thread"
        threadsNum = int(node["threads"].getValue())
        def gen(x): return Denoiser(
            x, imageFiles[x], outFiles[x], getStrength, useAlbedo, channelAlbedo, useNormal, channelNormal)
        locLast = 0
        locCurrent = threadsNum
        fileRange = range(len(imageFiles))
        print fileRange
        print "pass fileRange"
        threadRange = int(len(imageFiles) / threadsNum + 1)
        print "pass threadRange"
        for i in range(threadRange):
            print "prograss in set MutilRange"
            prosser = map(gen, [i for i in fileRange[locLast:locCurrent:]])
            print "pass MutilRange"
            locLast = locCurrent
            locCurrent += threadsNum
            for i in prosser:
                i.start()
                i.join()
