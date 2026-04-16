export default {
    props: ['members'],
    emits: ['export-pdf', 'show-modal-add', 'open-edit-member', 'delete-member'],
    data() {
        return {
            searchTerm: ''
        }
    },
    computed: {
        filteredMembers() {
            const term = this.searchTerm.toLowerCase();
            return this.members.filter(m => 
                m.status === 'Ativo' && 
                (m.name.toLowerCase().includes(term) || (m.whatsapp && m.whatsapp.includes(term)))
            );
        }
    },
    template: `
                <div class="space-y-6">
                    <div class="flex justify-between items-center mb-10">
                        <div class="flex items-center gap-6">
                            <h2 class="text-5xl font-black tracking-tight text-slate-900">Corpo de Membros</h2>
                            <div class="relative group mt-2">
                                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-indigo-500 transition-colors">🔍</span>
                                <input v-model="searchTerm" type="text" placeholder="Buscar por nome ou whatsapp..." class="bg-white border-2 border-slate-100 p-3 pl-12 rounded-2xl w-64 outline-none focus:border-indigo-500 focus:w-80 transition-all font-bold text-xs shadow-sm">
                            </div>
                        </div>
                        <div class="flex gap-3">
                            <button @click="$emit('export-pdf')" class="bg-slate-100 text-slate-600 px-6 py-4 rounded-2xl font-black">Exportar PDF 📄</button>
                            <button @click="$emit('show-modal-add')" class="bg-indigo-600 text-white px-8 py-4 rounded-2xl font-black shadow-lg">Novo Membro +</button>
                        </div>
                    </div>
                    <div class="bg-white rounded-[2rem] shadow-xl overflow-hidden border border-slate-100">
                        <table class="w-full text-left border-collapse">
                            <thead>
                                <tr class="bg-slate-50 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b">
                                    <th class="p-4">Nome / WhatsApp</th>
                                    <th class="p-4">Cargos & Funções</th>
                                    <th class="p-4">Endereço</th>
                                    <th class="p-4 text-center">Batismo</th>
                                    <th class="p-4 text-center">Recusas</th>
                                    <th class="p-4 text-right">Ações</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-50">
                                <tr v-for="m in filteredMembers" :key="m.id" class="hover:bg-indigo-50/20 transition-colors group">
                                    <td class="p-4">
                                        <div class="font-bold text-slate-800">{{m.name}}</div>
                                        <div class="text-slate-400 font-bold text-[10px] tracking-tight">📱 {{m.whatsapp}}</div>
                                    </td>
                                    <td class="p-4">
                                        <div v-if="m.positions && m.positions.length > 0" class="flex gap-1 flex-wrap">
                                            <span v-for="p in m.positions" :key="p.id" class="text-[8px] font-black bg-slate-100 text-slate-500 px-2 py-0.5 rounded uppercase border border-slate-200">{{p.name}}</span>
                                        </div>
                                        <div v-else class="text-slate-300 italic text-[9px] uppercase">Sem Funções</div>
                                    </td>
                                    <td class="p-4">
                                        <div class="text-[10px] text-slate-500 max-w-[150px] truncate" :title="m.endereco">{{m.endereco || '---'}}</div>
                                    </td>
                                    <td class="p-4 text-center">
                                        <div class="text-[10px] font-bold text-slate-600">{{m.data_batismo ? new Date(m.data_batismo).toLocaleDateString('pt-BR') : '---'}}</div>
                                    </td>
                                    <td class="p-4 text-center">
                                        <span :class="['text-[10px] font-black px-2 py-1 rounded-full', m.consecutive_refusals >= 3 ? 'bg-rose-100 text-rose-600' : 'bg-slate-100 text-slate-500']">
                                            {{m.consecutive_refusals}}
                                        </span>
                                    </td>
                                    <td class="p-4 text-right">
                                        <div class="opacity-0 group-hover:opacity-100 transition-opacity flex justify-end gap-1">
                                            <button @click="$emit('open-edit-member', m)" class="text-slate-400 hover:text-indigo-600 p-2" title="Editar">⚙️</button>
                                            <button @click="$emit('delete-member', m.id)" class="text-slate-400 hover:text-red-500 p-2" title="Excluir">🗑️</button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
    `
}
