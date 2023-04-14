from subprocess import check_output
import subprocess
import threading
import locale

#execute kubectl commands
def executeCmd(cmd):
    #TODO: if output is very long, this will hang until it is done
    output = ""
    try:
        output = check_output(cmd,shell=True,stderr=subprocess.STDOUT,timeout=30)
        output = output.decode('utf-8')
    except subprocess.CalledProcessError as E:
        output = E.output.decode('utf-8')
    except subprocess.TimeoutExpired as E:
        output = E.output.decode('utf-8')
        output = "TIMEOUT when executing %s\n\n%s" % (cmd, output)
    except:
        #catch all exception including decoding errors
        #assume decoding error
        system_encoding = locale.getpreferredencoding()
        output = output.decode(system_encoding)
        
    return output

def executeBackgroudCmd(cmd):
    '''Execute command in background thread. Does not print output.'''
    #Thanks go to: http://sebastiandahlgren.se/2014/06/27/running-a-method-as-a-background-thread-in-python/
    class BackgroundProcess(object):
        """ Background process  class
        The run() method will be started and it will run in the background
        """

        def __init__(self, cmd):
            self.cmd = cmd

            thread = threading.Thread(target=self.run, args=())
            thread.daemon = True                            # Daemonize thread
            thread.start()                                  # Start the execution

        def run(self):
            output = ""
            try:
                output = check_output(self.cmd,shell=True,stderr=subprocess.STDOUT,timeout=30)
                output = output.decode('utf-8')
            except subprocess.CalledProcessError as E:
                output = E.output.decode('utf-8')
            except subprocess.TimeoutExpired as E:
                output = E.output.decode('utf-8')
                output = "TIMEOUT when executing %s\n\n%s" % (cmd, output)

    BackgroundProcess(cmd)
    return "Delete pod started in background. Refresh pod list to see status."       
    

def deletePod(podName,namespace,force):
    cmd = f"kubectl delete pod {podName}"
    cmd = f"{cmd} -n {namespace}"
    if (force == True):
        cmd = f"{cmd} --grace-period=0 --force"
    return executeBackgroudCmd(cmd)


def describePod(podName,namespace,options):
    cmd = f"kubectl describe pod {podName}"
    cmd = f"{cmd} -n {namespace} {options}"
    return executeCmd(cmd)

def getPodYaml(podName,namespace):
    cmd = f"kubectl get pod {podName}"

    cmd = f"{cmd} -n {namespace}"
    cmd = f"{cmd} -o yaml "
    output = ""
    return executeCmd(cmd)

def getPodJSON(podName,namespace):
    cmd = f"kubectl get pod {podName}"

    cmd = f"{cmd} -n {namespace}"
    cmd = f"{cmd} -o json "
    output = ""
    return executeCmd(cmd)

def getPodLabels(podName,namespace):
    cmd = f"kubectl get pod {podName} -n {namespace} --show-labels"
    return executeCmd(cmd)

def getTop(podName,namespace,cmdString,isAllNamespaces=False):
    #cmd="kubectl top pods -n %s" % (podName, namespace)
    cmd=None
    if cmdString.find("-c") > -1:
        #show top of selected pod and containers
        cmd = f"kubectl top pod {podName} -n {namespace} --containers"

    if cmdString.find("-n") > -1:
        #show top of nodes
        cmd="kubectl top nodes"

    if cmdString.find("-l") > -1:
        #show top of given labels
        label=cmdString.split()[2]
        cmd = f"kubectl top pod  -n {namespace} -l {label}"

    if cmd is None:
        if isAllNamespaces==True:
            cmd="kubectl top pods --all-namespaces"
        else:
            cmd = f"kubectl top pods -n {namespace}"

    return executeCmd(cmd)


def execCmd(podName,namespace,command):
    cmd = f"kubectl exec {podName}"

    cmd = f"{cmd} -n {namespace}"
    if (command.find("-c")==0):
        #there is container
        commandList=command.split()
        #first is -c
        #second is container name
        containerName=commandList[1]
        cmd = f'{cmd} -c {containerName} -- {" ".join(commandList[2:])} '
    else:
        cmd = f"{cmd} -- {command}"
    return executeCmd(cmd)



def logsPod(podName,namespace,options):
    cmd = f"kubectl logs {podName}"
    cmd = f"{cmd} -n {namespace} {options}"
    return executeCmd(cmd)

def getNodes(noderole=None):
    #kubectl get nodes -l node-role.kubernetes.io/worker=true
    cmd="kubectl get nodes "
    if noderole != None:
        cmd = f"{cmd} -l node-role.kubernetes.io/{noderole}=true"
    return executeCmd(f"{cmd} --no-headers")

def describeNode(nodeName):
    cmd="kubectl describe node \"%s\" " % nodeName
    return executeCmd(cmd)

def getDescribeNodes(noderole=None):
    #kubectl get nodes -l node-role.kubernetes.io/worker=true
    cmd="kubectl describe nodes "
    if noderole != None:
        cmd = f"{cmd} -l node-role.kubernetes.io/{noderole}=true"
    return executeCmd(cmd)


def getPods(namespace,nodeNameList=[]):
    cmd="kubectl get pods "

    if namespace == "all-namespaces":
        cmd = f"{cmd}--{namespace}"
    else:
        cmd = f"{cmd}-n {namespace}"
    cmd += " -o wide "
    cmd += " --no-headers"
    output = ""
    if nodeNameList != None and len(nodeNameList)>0:
        #get pods for specified nodes
        for nodeName in nodeNameList:
            #kubectl get pods --all-namespaces  --no-headers --field-selector spec.nodeName=10.31.10.126
            cmd2 = f"{cmd} --field-selector spec.nodeName={nodeName}"
            output2 = executeCmd(cmd2)
            if output2.lower().find("no resources found") == -1:
                output = output + output2
    else:
        output = executeCmd(cmd)

    return output

def getNamespaces():
    namespaces=[]
    output = executeCmd("kubectl get namespaces --no-headers")
    for line in output.split('\n'):
        fields = line.split()
        if len(fields) > 0:
            namespaces.append(fields[0])
    return namespaces