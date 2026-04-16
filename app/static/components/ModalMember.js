export default {
    props: ['show', 'cargos', 'funcoes', 'getPosName', 'member', 'isEdit'],
    emits: ['close', 'save'],
    template: `
        <div v-if="show" class="fixed inset-0 modal-blur flex justify-center items-center z-[100] p-6">
            <div class="bg-white p-12 rounded-[3.5rem] shadow-2xl w-full max-w-2xl text-center overflow-y-auto max-h-[90vh]">
                <h3 class="text-3xl font-black mb-8 uppercase italic text-indigo-600">{{ isEdit ? 'Editar Membro' : 'Ficha de Membro' }}</h3>
                <div class="space-y-4 text-left grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="md:col-span-2">
                        <p class="text-[10px] font-black text-slate-400 uppercase mb-1 ml-2">Nome Completo</p>
                        <input v-model="member.name" type="text" placeholder="Nome Completo" class="w-full border-2 p-4 rounded-2xl font-bold outline-none bg-slate-50">
                    </div>
                    <div>
                        <p class="text-[10px] font-black text-slate-400 uppercase mb-1 ml-2">WhatsApp</p>
                        <input v-model="member.whatsapp" type="text" placeholder="Ex: 351912345678" class="w-full border-2 p-4 rounded-2xl font-bold outline-none bg-slate-50">
                    </div>
                    <div>
                        <p class="text-[10px] font-black text-slate-400 uppercase mb-1 ml-2">Data de Batismo</p>
                        <input v-model="member.data_batismo" type="date" class="w-full border-2 p-4 rounded-2xl font-bold outline-none bg-slate-50">
                    </div>
                    <div class="md:col-span-2">
                        <p class="text-[10px] font-black text-slate-400 uppercase mb-1 ml-2">Endereço Residencial</p>
                        <input v-model="member.endereco" type="text" placeholder="Rua, Número, Bairro..." class="w-full border-2 p-4 rounded-2xl font-bold outline-none bg-slate-50">
                    </div>
                    
                    <div>
                        <p class="text-[10px] font-black text-slate-400 uppercase mb-1 ml-2">Cargo Ministerial</p>
                        <select v-model="member.cargo_id" class="w-full border-2 p-4 rounded-2xl font-bold outline-none bg-slate-50">
                            <option value="">Nenhum</option>
                            <option v-for="c in cargos" :value="c.id">{{c.name}}</option>
                        </select>
                    </div>

                    <div>
                        <p class="text-[10px] font-black text-slate-400 uppercase mb-1 ml-2 italic">Gerenciar Funções na Escala ⬇️</p>
                        <div class="space-y-3">
                            <div class="relative">
                                <select @change="if($event.target.value) { if(!member.selectedFuncoes.includes(parseInt($event.target.value))) member.selectedFuncoes.push(parseInt($event.target.value)); $event.target.value=''; }" class="w-full border-2 p-4 rounded-2xl font-bold outline-none bg-slate-50 text-xs appearance-none focus:border-indigo-500">
                                    <option value="">Clique para selecionar/adicionar...</option>
                                    <option v-for="f in funcoes" :key="f.id" :value="f.id">{{f.name}}</option>
                                </select>
                                <span class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">▼</span>
                            </div>
                            
                            <div class="flex flex-wrap gap-2 min-h-[50px] p-3 border-2 border-dashed rounded-2xl bg-white">
                                <div v-for="fid in member.selectedFuncoes" :key="fid" class="bg-indigo-600 text-white px-3 py-1.5 rounded-xl text-[9px] font-black flex items-center gap-2 shadow-sm group">
                                    <span>{{ getPosName(fid) }}</span>
                                    <button @click="member.selectedFuncoes = member.selectedFuncoes.filter(id => id !== fid)" class="hover:text-red-300 transition-colors">×</button>
                                </div>
                                <div v-if="member.selectedFuncoes.length === 0" class="text-[9px] font-bold text-slate-300 uppercase italic p-1">Nenhuma função selecionada</div>
                            </div>
                        </div>
                    </div>

                    <div class="md:col-span-2 mt-4">
                        <button @click="$emit('save', member)" class="w-full bg-indigo-600 text-white py-6 rounded-[2rem] font-black text-xl shadow-xl hover:bg-indigo-700 transition-all">{{ isEdit ? 'Salvar Alterações 💾' : 'Finalizar Cadastro ✅' }}</button>
                        <button @click="$emit('close')" class="w-full text-slate-400 font-black text-xs uppercase mt-4">Cancelar</button>
                    </div>
                </div>
            </div>
        </div>
    `
}
