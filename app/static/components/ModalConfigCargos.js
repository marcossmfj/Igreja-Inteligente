const ModalConfigCargos = {
    template: `
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
            <!-- Header -->
            <div class="p-6 border-b flex justify-between items-center bg-gray-50">
                <div>
                    <h2 class="text-2xl font-bold text-gray-800">⚙️ Configurar Linguajar</h2>
                    <p class="text-sm text-gray-500 text-left">Personalize os Cargos e Funções da sua igreja</p>
                </div>
                <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 transition-colors">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>

            <!-- Body -->
            <div class="p-6 overflow-y-auto flex-1 bg-white">
                <!-- Formulário de Adição -->
                <div class="bg-blue-50 p-4 rounded-xl border border-blue-100 mb-6">
                    <h3 class="text-sm font-semibold text-blue-800 mb-3 text-left">Adicionar Novo Termo</h3>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <input v-model="newItem.name" type="text" placeholder="Ex: Diácono, Guitarrista..." 
                               class="md:col-span-1 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                        
                        <select v-model="newItem.type" class="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                            <option value="Cargo">Cargo (Eclesiástico)</option>
                            <option value="Função">Função (Serviço/Escala)</option>
                        </select>

                        <button @click="saveItem" :disabled="loading"
                                class="bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 transition-all flex items-center justify-center gap-2">
                            <i v-if="loading" class="fas fa-spinner animate-spin"></i>
                            <i v-else class="fas fa-plus"></i>
                            Adicionar
                        </button>
                    </div>
                </div>

                <!-- Lista de Itens -->
                <div class="space-y-4">
                    <div v-if="positions.length === 0" class="text-center py-10 text-gray-400">
                        <i class="fas fa-tags text-4xl mb-3 block"></i>
                        Nenhum termo cadastrado ainda.
                    </div>
                    
                    <div v-for="pos in sortedPositions" :key="pos.id" 
                         class="flex items-center justify-between p-4 border rounded-xl hover:bg-gray-50 transition-colors group">
                        <div class="flex items-center gap-4">
                            <span :class="pos.type === 'Cargo' ? 'bg-purple-100 text-purple-700' : 'bg-green-100 text-green-700'" 
                                  class="text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider">
                                {{ pos.type }}
                            </span>
                            <span class="font-semibold text-gray-700">{{ pos.name }}</span>
                        </div>
                        <button @click="deleteItem(pos.id)" class="text-red-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-all p-2">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="p-6 border-t bg-gray-50 flex justify-end">
                <button @click="$emit('close')" class="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg font-bold hover:bg-gray-300 transition-all">
                    Fechar
                </button>
            </div>
        </div>
    </div>
    `,
    props: ['positions'],
    data() {
        return {
            loading: false,
            newItem: {
                name: '',
                type: 'Cargo'
            }
        }
    },
    computed: {
        sortedPositions() {
            return [...this.positions].sort((a, b) => a.type.localeCompare(b.type));
        }
    },
    methods: {
        async saveItem() {
            if (!this.newItem.name) return alert("Digite o nome do cargo ou função!");
            this.loading = true;
            try {
                const response = await fetch('/members/positions', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}` 
                    },
                    body: JSON.stringify(this.newItem)
                });
                
                if (response.ok) {
                    this.$emit('refresh');
                    this.newItem.name = '';
                } else {
                    const errorData = await response.json();
                    alert("Erro ao salvar: " + (errorData.detail || "Verifique se o termo já existe."));
                }
            } catch (error) {
                console.error("Erro ao salvar:", error);
                alert("Erro de conexão com o servidor.");
            } finally {
                this.loading = false;
            }
        },
        async deleteItem(id) {
            if (!confirm("Tem certeza que deseja excluir este termo? Isso pode afetar os membros já cadastrados.")) return;
            try {
                const response = await fetch(`/members/positions/${id}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });
                if (response.ok) {
                    this.$emit('refresh');
                } else {
                    alert("Erro ao excluir. O termo pode estar em uso.");
                }
            } catch (error) {
                alert("Erro de conexão.");
            }
        }
    }
};

export default ModalConfigCargos;
