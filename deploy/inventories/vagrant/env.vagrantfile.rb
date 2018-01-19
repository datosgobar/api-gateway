VAGRANTFILE_API_VERSION = "2"

checkout_branch = ENV["CHECKOUT_BRANCH"]
ansible_limit = ENV["ANSIBLE_LIMIT"] || "all"

extra_vars = {}

if checkout_branch
  extra_vars["checkout_branch"] = checkout_branch
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "bento/ubuntu-16.04"
  config.ssh.forward_agent = true

  config.vm.define "kong0" do |web|
      web.vm.provider :virtualbox do |vb|
        vb.memory = 1024
        vb.cpus = 1
      end
      web.vm.network "private_network", ip: "192.168.35.60"
        web.vm.provision "ansible" do |ansible|
        ansible.compatibility_mode = "2.0"
        ansible.playbook = "site.yml"
        ansible.inventory_path = "inventories/vagrant/hosts"
        ansible.vault_password_file = "inventories/vagrant/vault_password.txt"

        ansible.verbose = "vvv"
        # ansible.tags = ["elastic"]
        ansible.limit = ansible_limit
        ansible.extra_vars = extra_vars
      end

  end

end
