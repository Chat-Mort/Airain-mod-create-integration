# Installe les écrans de Create validés (piste B, carter) et le réglage de valeur dans le pack d'interface HD
import ecrans, reglages
HD = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/create/textures/gui/'
FAITS = {'display_link': ecrans.lien_affichage_B, 'threshold_switch': ecrans.interrupteur_seuil_B, 'value_settings': reglages.reglages, 'sequencer': ecrans.engrenage_sequence, 'factory_gauge': ecrans.jauge_usine, 'requester': ecrans.demandeur, 'frogport_and_mailbox': ecrans.grenouille_boite, 'filters_2': ecrans.filtre_colis, 'assemble': ecrans.assemblage, 'curiosities_2': ecrans.telecommande_plan, 'stock_keeper_categories': ecrans.categories_gardien, 'schedule_2': ecrans.horaire_gare, 'curiosities': ecrans.curiosites}
if __name__ == '__main__':
    for n, f in FAITS.items(): f().save(HD + n + '.png'); print(n)

# Lot Numismatics (1.68.17) : écrans en carter, et l'engrenage séquencé étoffé
def installer_numismatics():
    import numis
    D = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/numismatics/textures/gui/'
    import os; os.makedirs(D, exist_ok=True)
    for n, f in numis.ECRANS.items(): f().save(D + n + '.png'); print(n)
    ecrans.engrenage_sequence().save(HD + 'sequencer.png'); print('sequencer')

# Lot 1.68.18 : widgets des recettes de Create (EMI) et table de décoration de Sophisticated Storage
def installer_lot_emi():
    import os, jei_create, deco_table
    R = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/'
    os.makedirs(R + 'create/textures/gui/jei', exist_ok=True); os.makedirs(R + 'sophisticatedstorage/textures/gui', exist_ok=True)
    jei_create.widgets().save(R + 'create/textures/gui/jei/widgets.png')
    deco_table.table_decoration().save(R + 'sophisticatedstorage/textures/gui/decoration_table.png')
