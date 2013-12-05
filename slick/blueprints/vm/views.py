from __future__ import division
import json

from flask import redirect, url_for, flash, request, render_template

from slick.utils.core import get_client
from slick.utils.nested_dict import lookup
from slick.utils.session import login_required
from .forms import CreateVMForm
from .manager import (all_instances, all_instance_options,
                      cancel_instance, change_port_speed,
                      get_instance, launch_instance,
                      reboot_instance, reload_instance,
                      validate_instance)


@login_required
def change_nic_speed(object_id, nic, speed):
    """ This function will alter the port speed of the specified NIC on the
    VM. It's designed to be called via AJAX.

    :param int object_id: The ID of the instance to change
    :param string nic: The identifier of the network interface to change
    :param int speed: The speed to change the interface to
    """

    (success, message) = change_port_speed(object_id, nic, speed)
    return json.dumps({'success': success, 'message': message})


@login_required
def cancel(vm_id):
    """ This function will cancel the specified virtual machine.

    :param int vm_id: The ID of the instance to change
    """

    (success, message) = cancel_instance(vm_id)
    return json.dumps({'success': success, 'message': message})


@login_required
def create():
    # Setup the form choices here since we need access to the client object
    # in order to do so.
    form = CreateVMForm()
    all_options = all_instance_options('')

    dc_options = [('', 'First Available')]
    dc_options += all_options['datacenter']
    form.datacenter.choices = dc_options

    os_options = [('', '-- Select --')] + all_options['os']
    form.os.choices = os_options

    cpu_options = [('', '-- Select --')] + all_options['cpus']
    form.cpus.choices = cpu_options

    ram_options = [('', '-- Select --')] + all_options['memory']
    form.memory.choices = ram_options

    if form.validate_on_submit():
        fields = {}
        for field in form:
            if 'csrf_token' == field.name:
                continue

            fields[field.name] = field.data

        (success, message) = launch_instance(**fields)
        if success:
            flash(message, 'success')

            if request.form.get('save_template'):
                template_name = request.form.get('template_title')

                fields['title'] = template_name
                _save_template(fields)

                flash('Configuration saved for future use.', 'success')

            return redirect(url_for(".index"))
        else:
            flash(message, 'error')

    if form.errors:
        flash('There are validation errors with your submission.', 'error')

    return render_template('vm_add.html', title='Create Instance', form=form)


@login_required
def get_password(object_id, username):
    """ This function is called via AJAX to retrieve the root/admin password
    for the specified machine and account.

    :param int object_id: The VM ID to retrieve the password for.
    :param string username: The specific admin account that owns the password.
    """

    instance = get_instance(object_id, True)

    if not instance:
        return 'Invalid account'

    password = 'Password not found'

    for account in lookup(instance, 'operatingSystem', 'passwords'):
        if username == account['username']:
            password = account['password']

    return password


@login_required
def hard_reboot_vm(vm_id):
    (success, message) = reboot_instance(vm_id, False)
    return json.dumps({'success': success, 'message': message})


@login_required
def index():
    account_obj = get_client()['Account']
    total_vms = account_obj.getCurrentUser(mask='mask[id,virtualGuestCount]')
    total_vms = total_vms.get('virtualGuestCount')

    instances = all_instances({})
    payload = {}
    payload['title'] = 'List Instances'
    payload['instances'] = instances
    payload['total_items'] = total_vms

    search = ''

    if request.args.get('dc'):
        search = request.args.get('dc')

    payload['search'] = search

    return render_template("vm_index.html", **payload)


@login_required
def price_check():
    form = CreateVMForm()

    fields = {}

    for field in form:
        if 'csrf_token' == field.name:
            continue

        if request.form.get(field.name):
            fields[field.name] = request.form[field.name]

    results = validate_instance(**fields)
    return render_template('vm_price_quote.html', order_template=results)


@login_required
def reload_vm(vm_id):
    (success, message) = reload_instance(vm_id)
    return json.dumps({'success': success, 'message': message})


@login_required
def soft_reboot_vm(vm_id):
    (success, message) = reboot_instance(vm_id)
    return json.dumps({'success': success, 'message': message})


@login_required
def start_vm(vm_id):
    vg_client = get_client()['Virtual_Guest']
    vg_client.powerOn(id=vm_id)
    return json.dumps({
        'success': True,
        'message': 'Instance is being started.'
    })


@login_required
def stop_vm(vm_id):
    vg_client = get_client()['Virtual_Guest']
    vg_client.powerOff(id=vm_id)
    return json.dumps({
        'success': True,
        'message': 'Instance is being stopped.'
    })


@login_required
def status(vm_id):
    if not vm_id:
        return None

    instance = get_instance(vm_id)
    if not instance:
        return ''

    html = render_template('vm_instance_row.html', instance=instance)

    return json.dumps({
        'active': instance['active'],
        'row_html': html,
    })


@login_required
def view(vm_id):
    instance = get_instance(vm_id)

    payload = {}
    payload['title'] = 'View VM'
    payload['subheader'] = instance['fqdn']
    payload['object'] = instance
    payload['module'] = 'vm_module'

    return render_template('shared/object_view.html', **payload)