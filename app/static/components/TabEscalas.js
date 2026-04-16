export default {
    props: ['groupedSchedules', 'editingId', 'getQualifiedMembers', 'positions'],
    emits: ['show-modal-template', 'show-modal-manual', 'show-modal-auto', 'send-event-notifications', 'open-quick-add', 'save-edit', 'remove-vaga', 'suggest-substitute', 'update:editingId'],
    methods: {
        openManual() { this.$emit('show-modal-manual'); },
        getWeekday(d) { return new Intl.DateTimeFormat('pt-BR', { weekday: 'long' }).format(new Date(d)).replace('-feira', ''); },
        getMonth(d) { return new Intl.DateTimeFormat('pt-BR', { month: 'short' }).format(new Date(d)).toUpperCase(); },
        getDay(d) { return new Date(d).getDate(); },
        formatTime(d) { return new Date(d).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }); }
    },
    template: `
                <div class="space-y-12">
                    <header class="flex justify-between items-center bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100">
                        <div>
                            <h2 class="text-5xl font-black tracking-tight">Escalas</h2>
                            <p class="text-slate-400 font-bold text-xs uppercase mt-2 tracking-widest italic">Inteligência Operacional</p>
                        </div>
                        <div class="flex gap-4">
                            <button @click="$emit('show-modal-template')" class="bg-white border-2 border-slate-200 text-slate-600 px-8 py-4 rounded-2xl font-black hover:bg-slate-50 transition-all flex items-center gap-2">
                                📋 Organogramas
                            </button>
                            <button id="btn-manual-escala" @click="openManual" class="bg-white border-2 border-slate-200 text-slate-600 px-8 py-4 rounded-2xl font-black hover:bg-slate-50 transition-all">Manual +</button>
                            <button @click="$emit('show-modal-auto')" class="bg-indigo-600 text-white px-8 py-4 rounded-2xl font-black shadow-xl hover:bg-indigo-700 transition-all flex items-center gap-2">
                                <span>Geração por IA</span>
                                <span class="bg-indigo-400 text-[10px] px-2 py-0.5 rounded-full">BETA</span>
                            </button>
                        </div>
                    </header>

                    <div v-for="(group, eventKey) in groupedSchedules" :key="eventKey" class="bg-white rounded-[2.5rem] shadow-xl border border-slate-100 overflow-hidden mb-10 service-card">
                        <div class="bg-slate-50 p-8 border-b flex justify-between items-center">
                            <div class="flex gap-6 items-center">
                                <div class="bg-indigo-600 text-white p-4 rounded-3xl font-black text-center min-w-[100px] shadow-lg shadow-indigo-100">
                                    <span class="text-[9px] block opacity-80 uppercase tracking-tighter">{{ getWeekday(group[0].event_date) }}</span>
                                    <span class="text-2xl block leading-none my-1">{{ getDay(group[0].event_date) }}</span>
                                    <span class="text-[10px] block opacity-70 uppercase">{{ getMonth(group[0].event_date) }}</span>
                                </div>
                                <div>
                                    <h3 class="text-2xl font-black text-slate-800">{{ group[0].event_name }}</h3>
                                    <p class="text-slate-400 font-bold text-xs uppercase tracking-widest mt-1 flex items-center gap-2">
                                        <span class="bg-slate-100 px-2 py-0.5 rounded text-slate-500">🕰️ {{ formatTime(group[0].event_date) }}</span>
                                        <span class="text-indigo-400">●</span>
                                        <span>{{ group.length }} Voluntários Escalados</span>
                                    </p>
                                </div>
                            </div>
                            <div class="flex gap-3">
                                <button @click="$emit('send-event-notifications', group[0])" class="bg-emerald-500 text-white px-6 py-3 rounded-2xl font-black shadow-lg flex items-center gap-2 hover:bg-emerald-600 transition-all">
                                    <span>📱 Enviar Convites (WhatsApp)</span>
                                </button>
                                <button @click="$emit('open-quick-add', group[0])" class="bg-white border-2 border-slate-200 px-6 py-3 rounded-2xl font-black shadow-sm hover:bg-slate-50 transition-all">+ Incluir</button>
                            </div>
                        </div>
                        
                        <div class="p-6">
                            <table class="w-full text-left">
                                <thead>
                                    <tr class="text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                        <th class="pb-4 px-4">Função</th>
                                        <th class="pb-4 px-4">Voluntário</th>
                                        <th class="pb-4 px-4 text-center">Status</th>
                                        <th class="pb-4 px-4 text-center">Zap</th>
                                        <th class="pb-4 px-4 text-right">Ações</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-50">
                                    <tr v-for="s in group" :key="s.id" class="group hover:bg-indigo-50/20 transition-colors">
                                        <td class="py-4 px-4">
                                            <span class="font-black text-[10px] uppercase bg-white border border-slate-200 px-3 py-1 rounded-lg text-slate-600 shadow-sm">{{ s.position?.name }}</span>
                                        </td>
                                        <td class="py-4 px-4">
                                            <div v-if="editingId === s.id" class="flex gap-2">
                                                <select v-model="s.member_id" class="text-xs p-2 border-2 rounded-xl bg-white font-bold border-indigo-200 outline-none">
                                                    <option v-for="m in getQualifiedMembers(s.position_id)" :value="m.id">{{m.name}}</option>
                                                </select>
                                                <button @click="$emit('save-edit', s)" class="bg-indigo-600 text-white px-3 rounded-lg font-black text-[10px]">OK</button>
                                            </div>
                                            <div v-else class="font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">{{ s.member?.name }}</div>
                                        </td>
                                        <td class="py-4 px-4 text-center">
                                            <span v-if="s.confirmed" class="text-[9px] font-black bg-emerald-100 text-emerald-600 px-3 py-1.5 rounded-full uppercase">Confirmado</span>
                                            <span v-else-if="s.rejected" class="text-[9px] font-black bg-rose-100 text-rose-600 px-3 py-1.5 rounded-full uppercase">Recusado</span>
                                            <span v-else class="text-[9px] font-black bg-amber-100 text-amber-600 px-3 py-1.5 rounded-full uppercase">Pendente</span>
                                        </td>
                                        <td class="py-4 px-4 text-center">
                                            <span v-if="s.notified" class="text-indigo-600 text-lg" title="Notificado">✅</span>
                                            <span v-else class="opacity-20 text-lg" title="Não enviado">📩</span>
                                        </td>
                                        <td class="py-4 px-4 text-right flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button @click="$emit('suggest-substitute', s)" class="bg-indigo-50 text-indigo-600 px-3 py-2 rounded-xl text-[10px] font-black hover:bg-indigo-100">✨ Sugestão</button>
                                            <button @click="$emit('update:editingId', s.id)" class="bg-slate-100 text-slate-600 px-3 py-2 rounded-xl text-[10px] font-black">Editar</button>
                                            <button @click="$emit('remove-vaga', s.id)" class="bg-rose-50 text-rose-500 px-3 py-2 rounded-xl text-[10px] font-black hover:bg-rose-100">Excluir</button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
    `
}
