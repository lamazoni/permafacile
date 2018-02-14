## Sujet
Il s'agit d'un genre d'agenda en ligne dont les fonctionnalités varient en fonction du rôle assigné à l'identifiant.

## Comment installer une version de développement
1. Pour avoir une installation locale rapidement sur ubuntu sur le port 8001 :

	```
		git clone https://github.com/lamazoni/permafacile
		cd permafacile
		sudo ./installDistriFacile.sh -a <ip>:8001 -u <user-linux>
	```

2. Initialisation de la base de donnée et population de donnée de test :

	```
		./setup.py
	```
3. Lancement du serveur de développement :

	```
		. ./bin/activate
		python run.py
	```

## Comment contribuer
Les contributions sont les bienvenues ! La méthode suivante sera probablement privilégiée :
	```
	git clone git@github.com:yourUserName/permafacile.git          # Clone your fork
	cd agenda                                                      # Change directory
	git remote add upstream https://github.com/lamazoni/permafacile.git # Assign original repository to a remote named 'upstream'
	git fetch upstream                                             # Pull in changes not present in your local repository
	git checkout -b my-new-feature                                 # Create your feature branch
	git commit -am 'Add some feature'                              # Commit your changes
	git push origin my-new-feature                                 # Push to the branch
	```
## Licence

[Peer Production License](https://wiki.p2pfoundation.net/Peer_Production_License "Wiki Peer Production License")
