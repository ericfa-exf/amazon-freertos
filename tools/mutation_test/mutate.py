"""
/*
 * Copyright (c) P. Arun Babu (www.linkedin.com/in/parunbabu)
 *
 * Permission to use, copy, modify, and distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */
"""

import os
import re
import sys
import random

import utils
import mutation_runner

### Mutation tricks ###

NULL_STRING = " "

mutation_selector = {
	"all" : {
		" < " : 
			[ " != ", " > ", " <= ", " >= ", " == " ],
		" > " : 
			[ " != ", " < ", " <= ", " >= ", " == " ],
		"<=" : 
			[ " != ", " < ", " > ", " >= ",  "==" ],
		">=" : 
			[ " != ", " < ", " <= ", " > ",  "==" ],
		"==" : 
			[ " != ", " = ", " < ",  " > ", " <= ", " >= " ],
		"!=" : 
			[ " == ", " = ", " < ",  " > ", " <= ", " >= " ],
		" = " : 
			[ " == ", " != ", " < ",  " > ", " <= ", " >= ", " = 0 * ", " = 0 ;//", " = NULL; //", " = ! " ],

		" + " : 
			[ " - ", " * ", " / ", " % " ],
		" - " : 
			[ " + ", " * ", " / ", " % " ],
		
		" * " : 
			[ " + ", " - ", " / ", " % " ],

		" / " : 
			[ " % ", " * ", " + ", " - " ],
		" % " : 
			[ " / ", " + ", " - ", " * " ],

		" + 1" :
			[ " - 1", "+ 0", "+ 2", "- 2" ],
		" - 1" :
			[ " + 1", "+ 0", "+ 2", "- 2" ],

		" & " : 
			[ " | ", " ^ " ],
		" | " : 
			[ " & ", " ^ " ],
		" ^ " : 
			[ " & ", " | " ],

		" &= " : 
			[ " |= ", " ^= " ],
		" |= " : 
			[ " &= ", " ^= " ],
		" ^= " : 
			[ " &= ", " |= " ],

		" ~" : 
			[ " !", NULL_STRING ],
		" !" : 
			[ " ~", NULL_STRING ],

		" && " : 
			[ " & ", " || "," && !" ],

		" || " :
			[ " | ", " && ", " || !" ],

		" >> " : " << ",
		" << " : " >> ",

		" << 1" :
			[ " << 0"," << -1", "<< 2" ],
		" >> 1" :
			[ " >> 0", " >> -1", ">> 2" ],

		"++" : "--",
		"--" : "++",

		"++;" : 
			[ "--;", "+=2;", "-=2;" ],
		"++)" : 
			[ "--)", "+=2)", "-=2)" ],
		"--;" : 
			[ "++;", "+=2;", "-=2;" ],
		"--)" : 
			[ "++)", "+=2)", "-=2)" ],

		" true "  :  " false ",
		" false " :  " true  ",

		"if (" :
			[ "if ( ! ", "if ( ~ ", "if ( 1 || ", "if ( 0 && " ],
		"while (" :
			[ "while ( ! ", "while ( ~ ", "while ( 0 && " , "// while (", " if (", "if (!"],
		
		"break;" : "{;}",
		"continue;" : "{;}",
		"goto " : "//goto ",

		"return " : 
			[ "return 0; //", "return 1; //", "return NULL; //", "return -1; //", "return 2* ", "return -1 * " ],


		# for embedded systems

		"0x00" :
			[ "0x01", "0x05", "0x0A", "0x0F", "0xAA", "0x55", "0xFF" ],
		"0x01 " :
			[ "0x00 ", "0x05 ", "0x0A ", "0x0F " ],
		"0x05 " :
			[ "0x00 ", "0x01 ", "0x0A ", "0x0F " ],
		"0x0A " :
			[ "0x00 ", "0x01 ", "0x05 ", "0x0F " ],
		"0x0F " :
			[ "0x00 ", "0x01 ", "0x05 ", "0x0A " ],


		"0x55 " :
			[ "0x00 ", "0xAA ", "0xFF " ],
		"0xAA " :
			[ "0x00 ", "0x55 ", "0xFF " ],
		"0xFF " :
			[ "0x00 ", "0x55 ", "0xAA " ],
		"[" :
			[ "[ -1 + ", "[ 1 + ", "[ 0 * " ],

		"(": " (! ",

		");":
			[ "*0);", "*-1);", "*2);" ],
		"," :
			[ ", ! ", ", 0 * ", ", -1 * ", ", 2 *" ],
		" ? " :
			[ " && 0 ? ", " || 1 ? " ],
		" int " :
			[" short int ", " char " ],
		" signed " : " unsigned ",
		" unsigned " : " signed ",
		" long " : 
			[ " int ", " short int ", " char " ],
		" float ": " int ",
		" double ": " int ",


		" free(": "// free(",

		"case ": "// case ",
		"default ": "// default ",

		# null terminate a string
		"\"": "\"\\0",

		"else {": "{",
		"else": "// else",
	}
}

mutation_trick = mutation_selector["all"]

def main (input_files, output_files = False, lines_to_mutate={}, rng=None) :
#
	# pick a random file
	src_index = rng.randint(0, len(input_files) - 1)
	source_file = input_files[src_index]
	source_code = open(source_file).read().split('\n')

	# if lines to mutate is unspecified, then choose from all lines
	number_of_lines_of_code = (len(lines_to_mutate[source_file]) if 
								lines_to_mutate[source_file] else len(source_code))
	# try mutating a random line
	random_line = rng.randint(0,number_of_lines_of_code)

	mutated_line = "" 
	for i in list(range(random_line,number_of_lines_of_code)) + list(range(0,random_line)):
	#
		# if lines to mutate is specified, use the index to choose from there instead
		line = (lines_to_mutate[source_file][i] if 
					lines_to_mutate[source_file] else i) - 1

		# get the list of mutant operators for this line
		mutation_trick = (mutation_selector[str(line + 1)] if 
							str(line + 1) in mutation_selector else mutation_selector["all"])
		# simulate random operators by shuffling, need to create a list first in case
		# this line doesn't have first operator in substring
		mutant_operators = list(mutation_trick.keys())
		rng.shuffle(mutant_operators)
		
		if lines_to_mutate[source_file] and max(lines_to_mutate[source_file]) >= len(source_code):
			raise mutation_runner.LineOutOfRange("Line is out of range of source")

		# do not mutate preprocessor or assert statements
		if source_code[line].strip().startswith("#") or source_code[line].strip().startswith("assert") :
			continue

		for m in mutant_operators :
		#
			# search for substrings we can mutate
			number_of_substrings_found = source_code[line].count(m)

			if number_of_substrings_found > 0 :
			#
				mutate_at_index = 0 
		
				# if more than one substrings are found
				# then : choose any one randomly

				random_substring = rng.randint(1,number_of_substrings_found)
				for r in range(1,random_substring+1) :
				#
					if mutate_at_index == 0 :
						mutate_at_index = source_code[line].index(m)
					else :
						mutate_at_index = source_code[line].index(m,mutate_at_index+1)
				#

				# if there is more than one way of mutating a substring
				# then : choose any one randomly
				if type(mutation_trick[m]) == str :
					mutate_with = mutation_trick[m]
				else :	
					mutate_with = mutation_trick[m][rng.randint(0,len(mutation_trick[m])-1)]

				sys.stderr.write("\n==> @ Line: "+str(line + 1)+"\n\n")
				sys.stderr.write("Original Line  : "+source_code[line].strip()+"\n")

				mutated_line = source_code[line][0:mutate_at_index] + source_code[line][mutate_at_index:].replace(m,mutate_with,1)

				sys.stderr.write("After Mutation : "+mutated_line.strip()+"\n")

				if output_files:
					write_to_file (output_files[src_index], source_code, line, mutated_line)
					sys.stderr.write("\nOutput written to "+output_files[src_index]+"\n")

				sys.stderr.write("\n")
				return src_index, source_code[line].strip(), mutated_line.strip(), line + 1
			#
		#
	#
	sys.stderr.write("Could not create a mutant. Please make sure it is a C file.\n")
	sys.stderr.write("You may need to indent your C file.\n")
	return src_index, "", "", -1
#

def write_to_file ( mutant_file_name, source_code, mutated_line_number, mutated_line ) :
#
	output_file = open(mutant_file_name, "w")

	for i in range(0,len(source_code)) :
		if i == mutated_line_number : 
			output_file.write("/* XXX: original code was : "+source_code[i]+" */\n")
			output_file.write(mutated_line+"\n")
		else :
			output_file.write(source_code[i]+"\n")

	output_file.close()
#

if __name__ == "__main__":
#
	if len(sys.argv) == 2: # For testing 
		main(sys.argv[1]) 

	elif len(sys.argv) == 3: 
		assert(sys.argv[1] != sys.argv[2]) # Input file and Output file cannot be same
		main(sys.argv[1],sys.argv[2]) 

	else:
		print("Usage: python mutate.py <file-to-mutate.c> [output-mutant-file-name.c]")
#
