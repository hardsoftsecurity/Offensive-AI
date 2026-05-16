import argparse
import sys
import tqdm

from LLMmap.inference import load_LLMmap
from LLMmap.dataset_maker import make_dataset_entries_for_new_llm
from LLMmap.prompt_configuration import PromptConfFactory, TRAIN
from LLMmap.llm import load_llm


def main():
    parser = argparse.ArgumentParser(description="Generate templates for a new LLM using LLMmap and add it to the template file.")
    parser.add_argument('new_llm_name', type=str, help='Name or path of the new LLM')
    parser.add_argument('new_llm_type', type=int, help='0:Hugging Face, 1:OpenAI, 2:Anthropic')
    
    parser.add_argument('--prompt_conf_path', type=str, default='./confs/prompt_configurations/', help='Path to prompt configuration directory')
    parser.add_argument('--llmmap_path', type=str, default='./data/pretrained_models/default/', help='Path to the pretrained LLMmap model')
    parser.add_argument('--num_prompt_confs', type=int, default=100, help='Number of prompt configurations to sample')

    args = parser.parse_args()

    conf, llmmap = load_LLMmap(args.llmmap_path)

    if not conf['is_open']:
        print("Applicable to only open-set inference model. Aborting...")
        sys.exit(1)

    if not llmmap.ready:
        print("No templates found for the model. Aborting...")
        sys.exit(1)

    if args.new_llm_name in llmmap.templates_map:
        print(f"Template for {args.new_llm_name} has already be computed. Aborting...")
        sys.exit(1)

    new_llm = load_llm(args.new_llm_name, args.new_llm_type)
    pc = PromptConfFactory(args.prompt_conf_path)
    prompt_confs = pc.sample(args.num_prompt_confs, pool=TRAIN)

    entries = make_dataset_entries_for_new_llm(new_llm, conf['queries'], prompt_confs)
    new_template = llmmap.compute_template(entries)
    llmmap.add_entry_and_save_templates(new_llm.llm_name, new_template)


if __name__ == '__main__':
    main()