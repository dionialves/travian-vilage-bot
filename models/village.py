import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

BUILDING = {
    '1': 'lumber',
    '2': 'clay',
    '3': 'iron',
    '4': 'crop',
    '10': 'warehouse',
    '11': 'Granary',
    '13': 'Smithy',
    '15': 'Main Building',
    '17': 'Marketplace',
    '18': 'Embassy',
    '19': 'Barracks',
    '20': 'Stable',
    '22': 'Academy',
    '23': 'Cranny',
    '25': 'Residence',
    '34': "Stonemason's Lodge"
}

TROOPS = {
    'Roman': {
        'Legionnaire': 't1',
        'Praetorian': 't2',
        'Imperian': 't3',
        'Equites Legati': '',
        'Equites Imperatoris': '',
        'Equites Caesaris': '',
        'Battering ram': '',
        'Fire Catapult': '',
        'Senator': '',
        'Settler': ''
    },
    'Teuton': {
        'Clubswinger': 't1',
        'Spearman': 't2',
        'Axeman': 't3',
        'Scout': 't4',
        'Paladin': '',
        'Teutonic Knight': '',
        'Ram': '',
        'Catapult': '',
        'Chief': '',
        'Settler': ''
    },
    'Gaul': {
        'Phalanx': 't1',
        'Swordsman': 't2',
        'Pathfinder': 't3',
        'Theutates Thunder': 't4',
        'Druidrider': '',
        'Haeduan': '',
        'Ram': '',
        'Trebuchet': '',
        'Chieftain': '',
        'Settler': ''
    },
    'Egyptian': {
        'Slave Militia': '',
        'Ash Warden': '',
        'Khopesh Warrior': '',
        'Sopdu Explorer': '',
        'Anhur Guard': '',
        'Resheph Chariot': '',
        'Ram': '',
        'Stone Catapult': '',
        'Nomarch': '',
        'Settler': ''
    },
    'Hun': {
        'Mercenary': '',
        'Bowman': '',
        'Spotter': '',
        'Steppe Rider': '',
        'Marksman': '',
        'Marauder': '',
        'Ram': '',
        'Catapult': '',
        'Logades': '',
        'Settler': ''
    }

}

class Village(object):
    def __init__(self):
        self.server = str()
        self.username = str()
        self.password = str()
        self.browser = None
        self.villages = {}
        self.fields = {}
        self.building_ordens = {}
        self.resources = {}
        self.order_queue = None
        self.troops = {}


    def instance_browser(self):
        """
        Essa função é responsável por inicializar a instancia do navegador
        """
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--headless=new")
        self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.browser.implicitly_wait(3)

    def login(self, server, username, password):
        """
        Essa função é responsável por logar na pagina do travian
        """
        self.instance_browser()
        
        self.server = server
        self.username = username
        self.password = password
        self.server = 'https://' + self.server

        self.browser.get(self.server)

        username = self.browser.find_element(By.NAME, 'name')
        password = self.browser.find_element(By.NAME, 'password')

        username.send_keys(self.username)
        password.send_keys(self.password)

        self.browser.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[2]/div[2]/div/div/div[1]/form/table/tbody/tr[5]/td[2]/button").click()

    def get_tribe(self):
        self.browser.get(f'{self.server}/profile')

        if self.browser.find_elements(By.CLASS_NAME, "gaul"):
            self.tribe = 'Gaul'
        elif self.browser.find_elements(By.CLASS_NAME, "teuton"):
            self.tribe = 'Teuton'
        else:
            self.tribe = 'Roman'


    def update_all_fields_village(self, village):
        """
            Atuliza todos os campos de construção da aldeia, do 1 ao 40. De uma aldeia em uma aldeia específica
        """
        fields = {}
        list_fields = []
        list_level = []
        list_slot_id = []
        list_building_id = []

        self.browser.get(self.villages[village]['url'])

        for x in range(1,41):
            self.browser.get(f'{self.server}/build.php?id={x}')

            # Obtem o Id do da construção
            url = self.browser.current_url.split('?')[1]
            slot_id = url.split('&')[0].split('=')[1]

            name = self.browser.find_elements(By.XPATH, '//*[@id="content"]/h1')[0].text

            if self.browser.find_elements(By.CLASS_NAME, 'buildingWrapper'):
                name_and_level = ['Zona Livre', '0']
                building_id = '0'
            else:
                name_and_level = self.separate_name(name)
                building_id = url.split('&')[1].split('=')[1]

            list_slot_id.append(slot_id)
            list_building_id.append(building_id)
            list_fields.append(name_and_level[0])
            list_level.append(name_and_level[1])

        fields['slot'] = list_slot_id
        fields['id'] = list_building_id
        fields['name'] = list_fields
        fields['level'] = list_level

        self.fields[village] = fields

    def update_fields_village(self, village, idsFields):
        """
            Atuliza os campos de construção da aldeia, conforme o id passado pela na função.
        """

        self.browser.get(self.villages[village]['url'])

        for id in idsFields:
            self.browser.get(f'{self.server}/build.php?id={id}')

            # Obtem o Id do da construção
            url = self.browser.current_url.split('?')[1]
            slot_id = url.split('&')[0].split('=')[1]
            building_id = url.split('&')[1].split('=')[1]

            # Pega o titulo da pagina para obter o level da construção
            name = self.browser.find_elements(By.XPATH, '//*[@id="content"]/h1')[0].text

            if self.browser.find_elements(By.CLASS_NAME, 'buildingWrapper'):
                name_and_level = ['Zona Livre', '0']
                building_id = '0'
            else:
                name_and_level = self.separate_name(name)

            self.fields[village]['slot'][int(id)-1] = slot_id
            self.fields[village]['id'][int(id)-1] = building_id
            self.fields[village]['name'][int(id)-1] = name_and_level[0]
            self.fields[village]['level'][int(id)-1] = name_and_level[1]


    def update_name_villages(self):
        """
        Autiliza o nome da aldeia e também sua URL de acesso
        """

        self.browser.get(self.server + '/dorf3.php')
        drive = self.browser.find_elements(By.XPATH, '//*[@id="sidebarBoxVillagelist"]/div[2]/div[2]')

        list_village = []
        if drive:
            drive = drive[0].text
            drive = drive.split('\n')

            for x in drive:
                aux = x.replace('\u202d', '').replace('\u202c', '')
                if aux and (aux[:1] != '('):
                    list_village.append(aux)

        for x in range(0, len(list_village)):

            xpathUrl = self.browser.find_element(By.XPATH, f'//*[@id="overview"]/tbody/tr[{x+1}]/td[1]/a')

            url = xpathUrl.get_attribute("href")
            id_village = url.split('=')[1]

            self.villages[list_village[x]] = {'url': url, 'id': id_village}

    def update_building_orders(self, village):
        """
        Escaneia de todas de uma ldeia específica as ordens de construção.
        """

        self.browser.get(self.villages[village]['url'])

        drive = self.browser.find_elements(By.XPATH, '//*[@id="contentOuterContainer"]/div/div[2]/div[1]/ul')

        orders = []
        if drive:
            # Ajustando string
            drive = drive[0].text
            drive = drive.split('\n')

            # Obtendo as informações da primeira ordem de construção
            orders.append(self.separate_name(drive[0]))
            orders[0].append(self.convert_string_to_secunds(drive[1]))

            # Obtendo informações da segunda ordem de construção
            if len(drive) == 4:
                orders.append(self.separate_name(drive[2]))
                orders[1].append(self.convert_string_to_secunds(drive[3]))

        self.building_ordens[village] = orders

    def get_resources(self, village):
        """
        Escaneia os recursos disponíveis em uma aldeia

        Criar um validador de informação, pois o recurso lumber esta retornando com a seguinte informação: \u202d2878\u202c
        """

        self.browser.get(self.villages[village]['url']) 

        self.browser.implicitly_wait(4)

        lumber = self.browser.find_element(By.ID, 'l1').text
        clay = self.browser.find_element(By.ID, 'l2').text
        iron = self.browser.find_element(By.ID, 'l3').text
        crop = self.browser.find_element(By.ID, 'l4').text

        self.resources[village] = {
            "lumber": lumber.replace(',', '').replace('.', '').replace(' ', ''),
            "clay": clay.replace(',', '').replace('.', '').replace(' ', ''),
            "iron": iron.replace(',', '').replace('.', '').replace(' ', ''),
            "crop": crop.replace(',', '').replace('.', '').replace(' ', '')
        }

    def upgrade_fields_resource(self, village, idField):
        """
        Nesta função realizaremos a construção ou o upgrade de recursos, recebendo a aldeia e o id do campo
        """

        self.browser.get(self.villages[village]['url'])
        self.browser.get(self.server + '/build.php?id=' + str(idField))
        buttonUpgrade = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[3]/div[3]/div[2]/div/div/div[3]/div[3]/div[1]/button')
        
        buttonUpgrade.click()

    def start_all_farm_list(self):
        """
        Nesta função iniciamos o assalto de todas as listas de farms contidas na aldeia
        """

        self.browser.get(self.server + '/build.php?id=39&gid=16&tt=99')

        buttonStartAllList = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[3]/div[3]/div[2]/div/div[3]/div/div[1]/div[2]/button[1]')
        buttonStartAllList.click()


    def check_construction_resources(self, idField):
        """
        Esta função checa se na aldeia tem os recursos necessários para a construção desejada
        """

        self.browser.get(self.server + '/build.php?id=' + str(idField))

        lumber = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[3]/div[3]/div[2]/div/div/div[3]/div[1]/div[1]/div[1]/span').text
        clay = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[3]/div[3]/div[2]/div/div/div[3]/div[1]/div[1]/div[2]/span').text
        iron = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[3]/div[3]/div[2]/div/div/div[3]/div[1]/div[1]/div[3]/span').text
        crop = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[3]/div[3]/div[2]/div/div/div[3]/div[1]/div[1]/div[4]/span').text

        lumber = lumber.replace(',', '').replace('.', '').replace(' ', '')
        clay = clay.replace(',', '').replace('.', '').replace(' ', '')
        iron = iron.replace(',', '').replace('.', '').replace(' ', '')
        crop = crop.replace(',', '').replace('.', '').replace(' ', '')

        return {'lumber': lumber, 'clay': clay, 'iron': iron, 'crop': crop}

    def get_only_crop(self, village):
        list_id_crop = []

        for x in range(0,40):
            id = self.fields[village]['id'][x]
            if id == '4':
                list_id_crop.append(self.fields[village]['slot'][x])

        return list_id_crop
    
    def get_no_crop(self, village):
        list_id_no_crop = []

        for x in range(0,40):
            id = self.fields[village]['id'][x]
            if id in ('1', '2', '3',):
                list_id_no_crop.append(self.fields[village]['slot'][x])

        return list_id_no_crop

    def check_resources_for_update_slot(self, name_village, id_field):
        # Atualiza os recursos da aldeia
        self.get_resources(name_village)

        # retorna lista com recursos necessários para fazer a construção
        resources = self.check_construction_resources(id_field)

        # Verifica se tem os rercursos necessário para fazer a construção
        if (int(self.resources[name_village]['lumber']) >= int(resources['lumber']) and
            int(self.resources[name_village]['clay']) >= int(resources['clay'])  and
            int(self.resources[name_village]['iron']) >= int(resources['iron'])  and
            int(self.resources[name_village]['crop']) >= int(resources['crop'])):
            return True
        else:
            return False

    def get_troops_infantary(self, village):
        if '19' in self.fields[village]['id']:
            self.browser.get(self.villages[village]['url'])

            slot_build = self.fields[village]['slot'][self.fields[village]['id'].index('19')]

            self.browser.get(f'{self.server}/build.php?id={slot_build}')

            infantry = []

            if self.tribe == 'Gaul':
                if self.browser.find_elements(By.NAME, "t1"):
                    infantry.append('Phalanx')

                if self.browser.find_elements(By.NAME, "t2"):
                    infantry.append('Swordsman')

            elif self.tribe == 'Teuton':
                if self.browser.find_elements(By.NAME, "t1"):
                    infantry.append('Clubswinger')

                if self.browser.find_elements(By.NAME, "t2"):
                    infantry.append('Spearman')

                if self.browser.find_elements(By.NAME, "t3"):
                    infantry.append('Axeman')

                if self.browser.find_elements(By.NAME, "t4"):
                    infantry.append('Scout')

            if self.tribe == 'Roman':
                if self.browser.find_elements(By.NAME, "t1"):
                    infantry.append('Legionnaire')

                if self.browser.find_elements(By.NAME, "t2"):
                    infantry.append('Praetorian')

                if self.browser.find_elements(By.NAME, "t3"):
                    infantry.append('Imperian')

            self.troops['infantry'] = infantry

    def get_troops_cavalry(self, village):
        if '20' in self.fields[village]['id']:
            self.browser.get(self.villages[village]['url'])

            slot_build = self.fields[village]['slot'][self.fields[village]['id'].index('20')]

            self.browser.get(f'{self.server}/build.php?id={slot_build}')

            cavalry = []
            if self.tribe == 'Gaul':
                if self.browser.find_elements(By.NAME, "t3"):
                    cavalry.append('Pathfinder')

                if self.browser.find_elements(By.NAME, "t4"):
                    cavalry.append('Theutates Thunder')

                if self.browser.find_elements(By.NAME, "t1"):
                    cavalry.append('')

                if self.browser.find_elements(By.NAME, "t2"):
                    cavalry.append('')


            elif self.tribe == 'Teuton':
                if self.browser.find_elements(By.NAME, "t1"):
                    cavalry.append('')

                if self.browser.find_elements(By.NAME, "t2"):
                    cavalry.append('')

            if self.tribe == 'Roman':
                if self.browser.find_elements(By.NAME, "t1"):
                    cavalry.append('')

                if self.browser.find_elements(By.NAME, "t2"):
                    cavalry.append('')

                if self.browser.find_elements(By.NAME, "t3"):
                    cavalry.append('')

            self.troops['cavalry'] = cavalry

    def train_infantry(self, village, infantry, train_number):
        if '19' in self.fields[village]['id']:
            self.browser.get(self.villages[village]['url'])

            slot_build = self.fields[village]['slot'][self.fields[village]['id'].index('19')]
            self.browser.get(f'{self.server}/build.php?id={slot_build}')

            code = TROOPS[self.tribe][infantry]

            input_number_of_troops = self.browser.find_element(By.NAME, code)
            input_number_of_troops.send_keys(train_number)

            button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[3]/div[3]/div[2]/div/div/form/button')
            button.click()

    def train_cavalry(self, village, cavalry, train_number):
        if '20' in self.fields[village]['id']:
            self.browser.get(self.villages[village]['url'])
            
            slot_build = self.fields[village]['slot'][self.fields[village]['id'].index('20')]
            self.browser.get(f'{self.server}/build.php?id={slot_build}')

            code = TROOPS[self.tribe][cavalry]

            input_number_of_troops = self.browser.find_element(By.NAME, code)
            input_number_of_troops.send_keys(train_number)

            button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[3]/div[3]/div[2]/div/div/form/button')
            button.click()

    def separate_name(self, name):
        """
        Utilitário para limpar a string recebida do site
        """
        result = []
        result.append(name[0:name.find('N')-1])
        result.append(name[len(name)-2:len(name)].split()[0])
        return result
    
    def convert_string_to_secunds(self, time):
        construction = time.split(':')
        secunds = (int(construction[0])*3600) + (int(construction[1])*60) + int(construction[2][0:2])

        return secunds

    def quit(self, *args):
        """
        Responsável por fechar o navegador interno
        """
        
        self.browser.get(f'{self.server}/logout')
        self.browser.quit()


if __name__ == '__main__':

    travian = Village()

    travian.server = 'ts3.x1.america.travian.com'
    travian.username = 'diviks'
    travian.password = 'alves625'

    village = 'Debian'

    travian.login(travian.server, travian.username, travian.password)
    travian.update_name_villages()
    travian.update_all_fields_village(village)
    travian.get_tribe()

    travian.get_troops_infantary(village)
    travian.get_troops_cavalry(village)



