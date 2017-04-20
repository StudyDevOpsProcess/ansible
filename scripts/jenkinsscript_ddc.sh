echo "Template ID = ${TEMPLATE_ID}"
echo "SDLC Env = ${ENVIRONMENT}"
echo "Service Tag = ${SERVICE_TAG}"

# define potential statuses for the 'failed' field
PENDING="pending"
WAITING="waiting"
RUNNING="running"
SUCCESS="successful"
FAILURE="failed"

counter=1

# launch job
output=$(tower-cli job launch --job-template=${TEMPLATE_ID} --extra-vars="ENVIRONMENT=${ENVIRONMENT} SERVICE_TAG=${SERVICE_TAG}")

# if job launch succeeds
if [[ $? -eq 0 ]]; then
    # get current job number
    currJob=$(echo "${output}" | awk '{print $1}' | tail -2 | head -1)
    echo "currJob number = ${currJob}"

    # get current job status
    status=$(tower-cli job status ${currJob} | awk '{print $1}' | tail -2 | head -1)

    # continue checking job status until it is determined
    if [[ ${status} == ${PENDING} || ${status} == ${WAITING} || ${status} == ${RUNNING} ]]; then
	if [[ ${counter} < 20 ]]; then
            echo -e "\nChecking Status"
            echo "----------------------------"
            while [[ ${status} == ${PENDING} || ${status} == ${WAITING} || ${status} == ${RUNNING} ]]; do
		sleep 5;
		status=$(tower-cli job status ${currJob} | awk '{print $1}' | tail -2 | head -1)
		echo "Attempt #${counter}: status = ${status}"
		((counter++))
            done
            echo -e "----------------------------"

	    if [[ ${status} == ${SUCCESS} ]]; then
		echo "Ansible job ran successfully! Please check the results at: http://ansible.autorunops.com:8080/#/jobs/${currJob}"
		exit 0
            elif [[ ${status} == ${FAILURE} ]]; then
		echo "Ansible job failed. Please check the results at: http://ansible.autorunops.com:8080/#/jobs/${currJob}"
		exit 1
            else
		echo "ERROR: Ansible job ran unsuccessfully with unexpected result ${status}. Please check the results at: http://ansible.autorunops.com:8080/#/jobs/${currJob}"
		exit 1
            fi
	fi
    elif [[ ${status} == ${SUCCESS} ]]; then
	echo "Ansible job ran successfully!"
	exit 0
    else
	echo "ERROR: Expected status 'pending' or 'waiting' or 'running' for launched job ${currJub} but detected status: ${status}"
	exit 1
    fi
fi