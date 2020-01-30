# coding=utf-8
from PIL import Image


def main():
    continuer = True
    # Tant que l'utilisateur ne stope pas le programe celui-ci reste en fonction
    while continuer:
        afficherOptions()
        saisieUtilisateur = input()

        # Si l'utilisateur choisi la premiere option alors le programme est en mode de creation d'une image
        if saisieUtilisateur == "1":
            print("Saisissez le nom de l'image d'entrée (sans extension et dans le même dossier) : ")
            saisieFirstImage = input()
            print("Saisissez le message à cacher : ")
            saisieMessage = input()
            print("Saisissez le nom de l'image de sortie (sans extension) : ")
            saisieSecondImage = input()
            hideMessageInImage(messageToBinary(saisieMessage), saisieFirstImage, saisieSecondImage)
            continuer = tryAgain()
        # Si l'utilisateur choisi la seconde option le programme est en mode d'extraction de donnees
        elif saisieUtilisateur == "2":
            print("Saisissez le nom de l'image qui contient du code caché (sans extension et dans le même dossier) : ")
            saisieImage = input()
            pic = Picture(saisieImage)
            text = extractionBinaryMessage(pic.pic)
            interpretationMessageExtrait = binaryToMessage(text)
            # Affichage du message trouvé, si il n'y a pas de message le programme se stope
            print("Le message trouvé est : " + interpretationMessageExtrait)
            continuer = tryAgain()
        # La valeur 3 stope le programme
        elif saisieUtilisateur == "3":
            continuer = False
        else:
            continuer = True

# Fonction qui s'execute à la fin de chaque choix
def tryAgain():
    print("Voulez-vous continuer (O/N) ?")
    saisie = input()
    if saisie.capitalize() == "O":
        return True
    else:
        return False

# Fonction qui permet d'afficher les choix possibles
def afficherOptions():
    print("Choisissez l'option à faire : ")
    print("1 - Cacher un message dans une image")
    print("2 - Trouver le message caché dans une image")
    print("3 - Quitter")


# Class qui gere les images
class Picture:
    # Constructeur de l'image
    def __init__(self, picName="image"):
        self.pic = Image.open("./assets/" + picName + ".png")
        self.width = self.pic.width
        self.height = self.pic.height

    # Affiche les proprietes de l'image ouverte
    def displayProperties(self):
        print("Propriétés de l'image : ")
        print(self.pic.format + " - %d x %d" % self.pic.size + ' ' + self.pic.mode)

    # Creation d'une image aux memes dimensions que l'image ouverte et sur fond noir
    def createPic(self):
        return Image.new('RGB', (self.width, self.height), (0, 0, 0))

# Conversion d'un message texte en UTF8 en binaire
def messageToBinary(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

# Conversion du message en binaire
def binaryToMessage(text, encoding='utf-8', errors='surrogatepass'):
    n = int(text, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'

# Fonction qui cache le message dans l'image
# Prend en paramètre le message en binaire, le nom de l'image d'origine et le nom de l'image à sauvegarder
def hideMessageInImage(message, firstPicName, secondPicName):
    # Ouverture de l'image d'origine avec le nom fourni en paramètre
    pic1 = Picture(firstPicName)
    # Affichage des propriétés de l'image
    pic1.displayProperties()
    # Création d'une seconde image aux dimensions de celle d'origine
    pic2 = Picture.createPic(pic1)
    # Message en binaire restant à cacher dans l'image
    remainingMessageToHide = message

    # Balayage des pixels dans l'image
    for horizontal in range(0, pic1.width):
        for vertical in range(0, pic1.height):
            # Récupération des coordonnées actuelles
            coordonnees = horizontal, vertical
            # Récupération du pixel courant
            pixel = pic1.pic.getpixel(coordonnees)
            # Récupération de la valeur du pixel rouge
            pxRouge = pixel[0]
            # Conversion du pixel rouge en binaire
            # Suppression des deux premiers caractères (ex : on récupère 0b11001011 donc on veut enlever le 0b)
            binaryPxRouge = bin(pxRouge)[2:]
            # Formatage du binaire sur huit bits : 1 -> 00000001
            binaryRouge = format(int(binaryPxRouge), '08d')
            # Conservation des sept bits a gauche
            binaryRouge = binaryRouge[:7]
            # Concaténation des septs bits à gauche avec le bit à gauche de remainingMessageToHide s'il n'est pas vide
            # On met 0 s'il n'y a plus rien à écrire afin de pouvoir retrouver le message caché
            binaryRouge += remainingMessageToHide[0:1] if remainingMessageToHide != "" else "0"
            # Suppression du bit à gauche de remainingMessageToHide
            remainingMessageToHide = remainingMessageToHide[1:]
            # Remplacement dans la nouvelle image des pixels rouge modifiés et copie exacte des pixels vert et bleu
            pic2.putpixel(coordonnees, (int(binaryRouge, 2), pixel[1], pixel[2]))
    # Enregistrement de la nouvelle image avec les donnees
    pic2.save("./assets/" + secondPicName + ".png")
    # Affichage de l'image
    pic2.show()
    return pic2

# Extraction du message en binaire dans l'image passée en paramètre
def extractionBinaryMessage(pic):
    # Initialisation des variables à 0 ou string vide
    messageExtracted = ""
    messageTemp = ''
    index = 0
    code = 0
    # Balayage des pixels dans l'image
    for horizontal in range(0, pic.width):
        for vertical in range(0, pic.height):
            # Incrémentation de l'index pour savoir sur quel bit on se trouve
            index += 1
            # Récupération des coordonnées actuelles
            coordonnes = horizontal, vertical
            # Récupération du pixel courant
            pixel = pic.getpixel(coordonnes)
            # Récupération de la valeur du pixel rouge
            pxRouge = pixel[0]
            # Formattage de la valeur du pixel rouge en binaire sur 8 bits
            binaryRouge = format(int(bin(pxRouge)[2:]), '08d')
            # Récupération du LSB du pixel rouge si on a bien un binaire, 0 sinon
            lsbRouge = int(str(binaryRouge)[7:] if str(binaryRouge)[7:] != '' else "0")
            # Ajout de la valeur du LSB rouge à code pour savoir si on a bien trouvé un bit à 1 sur les 8 bits parcourus
            code += lsbRouge
            # Si on est en dessous du 8ème bit
            if index < 8:
                # On ajoute le LSB au message temporaire
                messageTemp += str(lsbRouge)
            # Sinon si on est arrivé au 8ème bit et que le code est différent de 0 (au moins un LSB = 1)
            elif index == 8 and code != 0:
                # On ajoute le message temporaire au message extrait en ajoutant le dernier LSB non concaténé
                messageExtracted += messageTemp + str(lsbRouge)
                # Réinitialisation des variables d'incrémentation
                index = 0
                code = 0
                messageTemp = ''

    return messageExtracted


# Appel de la fonction main
main()
