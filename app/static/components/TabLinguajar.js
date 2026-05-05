export default {
    props: ['positions'],
    emits: ['refresh'],
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
            // Garante que 'this.positions' seja tratado como array antes da ordenação
            const pos = Array.isArray(this.positions) ? this.positions : [];
            return [...pos].sort((a, b) => {
                const typeA = a.type || "";
                const typeB = b.type || "";
                return typeA.localeCompare(typeB);
            });
        }
    },
    template: `
    <div class="space-y-6">
        <div class="flex justify-between items-center mb-10">
            <div>
                <h2 class="text-5xl font-black tracking-tight text-slate-900">Linguajar</h2>
                <p class="text-slate-500 font-bold mt-2">Personalize os termos e cargos exclusivos da sua igreja.</p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Formulário de Cadastro -->
            <div class="lg:col-span-1">
                <div class="bg-white p-8 rounded-[2rem] shadow-xl border border-slate-100 sticky top-24">
                    <h3 class="text-xl font-black text-slate-800 mb-6 uppercase tracking-tighter italic">Novo Termo</h3>
                    <div class="space-y-4">
                        <div>
                            <label class="text-[10px] font-black text-slate-400 uppercase ml-2 mb-1 block">Nome do Cargo/Função</label>
                            <input v-model="newItem.name" type="text" placeholder="Ex: Diácono, Guitarrista..." 
                                   class="w-full bg-slate-50 border-2 border-slate-100 p-4 rounded-2xl outline-none focus:border-indigo-500 font-bold text-sm transition-all">
                        </div>
                        
                        <div>
                            <label class="text-[10px] font-black text-slate-400 uppercase ml-2 mb-1 block">Tipo de Termo</label>
                            <select v-model="newItem.type" class="w-full bg-slate-50 border-2 border-slate-100 p-4 rounded-2xl outline-none focus:border-indigo-500 font-bold text-sm appearance-none">
                                <option value="Cargo">Cargo (Eclesiástico)</option>
                                <option value="Função">Função (Escala/Serviço)</option>
                            </select>
                        </div>

                        <button @click="saveItem" :disabled="loading"
                                class="w-full bg-indigo-600 text-white py-5 rounded-2xl font-black text-lg shadow-lg shadow-indigo-100 hover:bg-indigo-700 transition-all flex items-center justify-center gap-2">
                            <span v-if="loading">Salvando...</span>
                            <span v-else>Cadastrar Termo</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Listagem -->
            <div class="lg:col-span-2">
                <div class="bg-white rounded-[2rem] shadow-xl border border-slate-100 overflow-hidden">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-slate-50 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b">
                                <th class="p-6">Termo</th>
                                <th class="p-6 text-center">Classificação</th>
                                <th class="p-6 text-right">Ações</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-50">
                            <tr v-for="pos in sortedPositions" :key="pos.id" class="hover:bg-slate-50/50 transition-colors group">
                                <td class="p-6">
                                    <div class="font-bold text-slate-800 text-lg">{{ pos.name }}</div>
                                </td>
                                <td class="p-6 text-center">
                                    <span :class="pos.type === 'Cargo' ? 'bg-purple-100 text-purple-700' : 'bg-emerald-100 text-green-700'" 
                                          class="text-[10px] font-black px-4 py-2 rounded-full uppercase tracking-wider">
                                        {{ pos.type }}
                                    </span>
                                </td>
                                <td class="p-6 text-right">
                                    <button @click="deleteItem(pos.id)" class="text-slate-300 hover:text-rose-500 transition-colors p-2">
                                        <i class="fas fa-trash-alt text-xl"></i>
                                        <span class="text-sm font-black ml-2">Excluir</span>
                                    </button>
                                </td>
                            </tr>
                            <tr v-if="positions.length === 0">
                                <td colspan="3" class="p-20 text-center text-slate-300">
                                    <div class="text-5xl mb-4">🏷️</div>
                                    <div class="font-black uppercase text-xs tracking-widest">Nenhum termo personalizado ainda</div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    `,
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
                if(response.ok) {
                    this.newItem.name = '';
                    this.$emit('refresh');
                    alert("Cadastrado com sucesso!");
                } else {
                    const errorData = await response.json();
                    alert("Erro ao salvar: " + (errorData.detail || "Verifique se este nome já existe."));
                }
            } catch (error) {
                alert("Erro de conexão com o servidor.");
            } finally {
                this.loading = false;
            }
        },
        async deleteItem(id) {
            if (!confirm("Tem certeza? Isso pode afetar os membros que já usam este termo.")) return;
            try {
                const response = await fetch(`/members/positions/${id}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });
                if(response.ok) this.$emit('refresh');
                else alert("Erro ao excluir. O termo pode estar sendo usado em escalas.");
            } catch (error) {
                alert("Erro de conexão.");
            }
        }
    }
};
