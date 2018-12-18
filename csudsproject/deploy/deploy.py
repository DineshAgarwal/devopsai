import azureml
from azureml.core import Workspace, Run
from azureml.core.conda_dependencies import CondaDependencies 
from azureml.core.webservice import AciWebservice
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.webservice import Webservice
from azureml.core.image import ContainerImage


# display the core SDK version number
print("Azure ML SDK Version: ", azureml.core.VERSION)

from azureml.core import Workspace
from azureml.core.model import Model

# Define Vars < Change the vars>
tenant_id="<Enter Your Tenant Id>"
app_id="<Application Id of the SPN you Create>"
app_key= "<Key for the SPN>"
workspace="<Name of your workspace>"
subscription_id="<Subscription id>"
resource_grp="<Name of your resource group where aml service is created>"

print("Starting to download the model file")
    
# Start creating 
# Point file to conf directory containing details for the aml service
spn = ServicePrincipalAuthentication(tenant_id,app_id,app_key)
ws = Workspace(auth = spn,
            workspace_name = workspace,
            subscription_id = subscription_id,
            resource_group = resource_grp)
model=Model(ws,'csu_sklearn_mnist')
model.download(target_dir = '.')
import os 
# verify the downloaded model file
os.stat('./csu_sklearn_mnist_model.pkl')
print("Downloaded Model File")

print("Writing Conda File")
myenv = CondaDependencies()
myenv.add_conda_package("scikit-learn")


with open("myenv.yml","w") as f:
    f.write(myenv.serialize_to_string())
print("Finished Writing Conda File")

print("Defined deploy configuration for ACI")
aciconfig = AciWebservice.deploy_configuration(cpu_cores=1, 
                                               memory_gb=1, 
                                               tags={"data": "MNIST",  "method" : "sklearn"}, 
                                               description='Predict MNIST with sklearn')    


print("Configuring Image")
# configure the image
image_config = ContainerImage.image_configuration(execution_script="score.py", 
                                                  runtime="python", 
                                                  conda_file="myenv.yml")

service = Webservice.deploy_from_model(workspace=ws,
                                       name='sklearn-mnist-svc',
                                       deployment_config=aciconfig,
                                       models=[model],
                                       image_config=image_config)

service.wait_for_deployment(show_output=True)

print(service.scoring_uri)