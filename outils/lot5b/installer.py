# Installe les écrans de Create validés (piste B, carter) et le réglage de valeur dans le pack d'interface HD
import ecrans, reglages
HD = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/create/textures/gui/'
FAITS = {'display_link': ecrans.lien_affichage_B, 'threshold_switch': ecrans.interrupteur_seuil_B, 'value_settings': reglages.reglages, 'sequencer': ecrans.engrenage_sequence, 'factory_gauge': ecrans.jauge_usine}
if __name__ == '__main__':
    for n, f in FAITS.items(): f().save(HD + n + '.png'); print(n)
